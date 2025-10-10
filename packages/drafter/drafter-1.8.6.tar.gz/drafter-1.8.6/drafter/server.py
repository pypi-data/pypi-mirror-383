import html
import os
import traceback
from dataclasses import dataclass, asdict, replace, field, fields
from functools import wraps
from typing import Any, Optional, List, Tuple, Union
import json
import inspect
import pathlib

import bottle

from drafter import friendly_urls, PageContent
from drafter.configuration import ServerConfiguration
from drafter.constants import RESTORABLE_STATE_KEY, SUBMIT_BUTTON_KEY, PREVIOUSLY_PRESSED_BUTTON
from drafter.debug import DebugInformation
from drafter.setup import Bottle, abort, request, static_file
from drafter.history import VisitedPage, rehydrate_json, dehydrate_json, ConversionRecord, UnchangedRecord, get_params, \
    remap_hidden_form_parameters, safe_repr
from drafter.page import Page
from drafter.files import TEMPLATE_200, TEMPLATE_404, TEMPLATE_500, INCLUDE_STYLES, TEMPLATE_200_WITHOUT_HEADER, \
    TEMPLATE_SKULPT_DEPLOY, seek_file_by_line
from drafter.raw_files import get_raw_files, get_themes
from drafter.urls import remove_url_query_params, is_external_url
from drafter.image_support import HAS_PILLOW, PILImage

import logging
logger = logging.getLogger('drafter')


SiteInformationType = Union[str, list, tuple, PageContent]
@dataclass
class SiteInformation:
    author: SiteInformationType
    description: SiteInformationType
    sources: SiteInformationType
    planning: SiteInformationType
    links: SiteInformationType

DEFAULT_ALLOWED_EXTENSIONS = ('py', 'js', 'css', 'txt', 'json', 'csv', 'html', 'md')

def bundle_files_into_js(main_file, root_path, allowed_extensions=DEFAULT_ALLOWED_EXTENSIONS):
    """
    Bundles all files from a specified directory into a JavaScript-compatible format
    for Skulpt, a Python-to-JavaScript transpiler. The function traverses through the
    given directory, reads files with extensions present in the allowed extensions list,
    and aggregates them into a JavaScript code snippet. It also identifies files to be
    skipped and keeps a record of successfully added files.

    :param main_file: The path to the main Python file. This file will be labeled
        as "main.py" in the JavaScript output.
    :type main_file: str
    :param root_path: The root directory to search for files.
    :type root_path: str
    :param allowed_extensions: A collection of file extensions allowed for inclusion
        in the final JavaScript output. Defaults to a predefined set.
    :type allowed_extensions: set[str]
    :return: A tuple containing:
        - The combined JavaScript output string with file contents.
        - A list of skipped files that do not match the allowed extensions.
        - A list of added files that were successfully bundled.
    :rtype: tuple[str, list[str], list[str]]
    """
    skipped_files, added_files = [], []
    all_files = {}
    for root, dirs, files in os.walk(root_path):
        for file in files:
            is_main = os.path.join(root_path, file) == main_file
            path = pathlib.Path(os.path.join(root, file)).relative_to(root_path)
            if pathlib.Path(file).suffix[1:].lower() not in allowed_extensions:
                skipped_files.append(os.path.join(root, file))
                continue
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                content = f.read()
                filename = str(path.as_posix()) if not is_main else "main.py"
                all_files[filename] = content
                added_files.append(os.path.join(root, file))

    js_lines = []
    for filename, contents in all_files.items():
        js_lines.append(f"Sk.builtinFiles.files[{filename!r}] = {contents!r};\n")

    return "\n".join(js_lines), skipped_files, added_files


def protect_script_tags(content: str) -> str:
    """
    Protects `<script>` tags in the given HTML content by escaping them. This is
    particularly useful when embedding HTML content within JavaScript strings, as
    unescaped `<script>` tags can lead to unintended script execution or parsing
    issues.

    :param content: The HTML content containing potential `<script>` tags.
    :type content: str
    :return: The modified HTML content with `<script>` tags escaped.
    :rtype: str
    """
    return content.replace("<script", "&lt;script").replace("</script>", "&lt;/script&gt;")


class Server:
    """
    Represents a server capable of managing routes, states, configurations, and error handling
    while supporting application setup and runtime logic.

    This class allows the definition of web routes, manages application states, handles errors
    gracefully, and provides a framework for deploying a web application with a structured
    configuration and support for image serving. It integrates with the Bottle framework
    to handle HTTP requests and responses.

    :ivar routes: A dictionary mapping URLs to their respective handler functions.
    :type routes: dict
    :ivar _handle_route: Internal mapping for handler functions and their respective URLs.
    :type _handle_route: dict
    :ivar configuration: The configuration object representing server settings.
    :type configuration: ServerConfiguration
    :ivar _state: Current state of the application.
    :type _state: Any
    :ivar _initial_state: Serialized representation of the initial application state.
    :type _initial_state: str
    :ivar _initial_state_type: Type of the initial state.
    :type _initial_state_type: type
    :ivar _state_history: List tracking historical states of the application.
    :type _state_history: list
    :ivar _state_frozen_history: List storing serialized snapshots of historical states.
    :type _state_frozen_history: list
    :ivar _page_history: History of visited pages.
    :type _page_history: list
    :ivar _conversion_record: Internal record tracking parameter conversion processes.
    :type _conversion_record: list
    :ivar original_routes: List containing tuples of original route URLs and their handlers.
    :type original_routes: list
    :ivar app: The Bottle application instance for handling HTTP requests.
    :type app: Bottle or None
    :ivar _custom_name: Custom name for the server instance, used in string representations.
    :type _custom_name: str or None
    """
    _page_history: List[Tuple[VisitedPage, Any]]
    _custom_name = None

    def __init__(self, _custom_name=None, **kwargs):
        self.routes = {}
        self._handle_route = {}
        self.configuration = ServerConfiguration(**kwargs)
        self._state = None
        self._initial_state = None
        self._initial_state_type = None
        self._state_history = []
        self._state_frozen_history = []
        self._page_history = []
        self._conversion_record = []
        self._site_information = None
        self.original_routes = []
        self.app = None
        self._custom_name = _custom_name

    def set_information(self, **kwargs):
        self._site_information = SiteInformation(**kwargs)

    def __repr__(self):
        """
        Provides a string representation of the current server object. If a custom
        name has been defined for the server instance, it returns that custom name.
        Otherwise, it provides a formatted string representation of the server's
        configuration.

        :return: The custom name of the server if defined, otherwise a string
            representation of the server's configuration.
        :rtype: str
        """
        if self._custom_name:
            return self._custom_name
        return f"Server({self.configuration!r})"

    def clear_routes(self):
        """
        Clears all stored routes from the `routes` attribute.

        This method removes all data within the `routes` attribute,
        resetting it back to its empty state. Use this when you want
        to remove all previous route configurations or stored paths
        within the object.
        """
        self.routes.clear()

    def dump_state(self):
        """
        Converts the current internal state of the State object into a JSON-encoded
        string. The internal state must be dehydratable using the provided
        utility function `dehydrate_json`.

        :raises TypeError: If any part of the internal state cannot be
            serialized into JSON due to invalid types.
        :raises ValueError: If serialization encounters unexpected value
            constraints or data inconsistencies.

        :return: A JSON string capturing the serialized format of the
            object's state.
        :rtype: str
        """
        return json.dumps(dehydrate_json(self._state))

    def load_from_state(self, state, state_type):
        """
        Loads a specific State object from a serialized state based on the given state type.
        This method takes a serialized JSON string representation of a state and
        rehydrates it into the corresponding Python object according to the given state type.

        :param state: The serialized JSON string representation of the object state.
        :type state: str
        :param state_type: The class or data type to rehydrate the JSON state into.
        :type state_type: Type
        :return: The rehydrated Python object based on the state and state_type.
        :rtype: Any
        """
        return rehydrate_json(json.loads(state), state_type)

    def restore_state_if_available(self, original_function):
        """
        Restores the state if the necessary data is available in the parameters. This
        function checks for the presence of a specific key in the parameters and, when
        available, rehydrates the serialized state back to the appropriate type and
        assigns it to the current instance's state.

        :param original_function: The function whose state is being restored. This function
                                  must have a parameter named `state` with an associated
                                  type annotation.
        :return: None
        """
        params = get_params()
        if RESTORABLE_STATE_KEY in params:
            # Get state
            old_state = json.loads(params.pop(RESTORABLE_STATE_KEY))
            # Get state type
            parameters = inspect.signature(original_function).parameters
            if 'state' in parameters:
                state_type = parameters['state'].annotation
                self._state = rehydrate_json(old_state, state_type)
                self.flash_warning("Successfully restored old state: " + repr(self._state))

    def add_route(self, url, func):
        """
        Adds a route to the routing table for URL handling, ensuring the URL is unique
        and maps a function to the given route. Prepares the URL, processes the
        function into a valid callable, and stores the mapping for later resolution
        when the URL is accessed.

        :param url: The URL string to be added as a route. It must be unique.
        :type url: str
        :param func: The function to be associated with the provided URL. This
            function will be called when the route is accessed.
        :type func: Callable
        :raises ValueError: If the URL is already registered for another function.
        :return: None
        """
        if url in self.routes:
            raise ValueError(f"URL `{url}` already exists for an existing routed function: `{func.__name__}`")
        self.original_routes.append((url, func))
        url = friendly_urls(url)
        func = self.make_bottle_page(func)
        self.routes[url] = func
        self._handle_route[url] = self._handle_route[func] = func

    def reset(self):
        """
        Resets the current State object to its initial configuration and clears all
        recorded histories. After resetting, the function returns the result of the
        route mapped to '/' (the root index URL).

        :return: The result of the '/' route execution.
        :rtype: Page
        """
        self._state = self.load_from_state(self._initial_state, self._initial_state_type)
        self._state_history.clear()
        self._state_frozen_history.clear()
        self._page_history.clear()
        self._conversion_record.clear()
        return self.routes['/']()

    # Helper function to render different SiteInformationType values
    def render_site_info(self, value: SiteInformationType) -> str:
        if isinstance(value, PageContent):
            # If it's PageContent, render it using its render method
            return value.render(self._state, self.configuration)
        elif isinstance(value, (list, tuple)):
            # If it's a list/tuple of strings, render as an unordered list with links converted to <a> tags
            items = []
            for item in value:
                if isinstance(item, str):
                    # Check if the item looks like a URL
                    if is_external_url(item):
                        items.append(f'<a href="{html.escape(item)}">{html.escape(item)}</a>')
                    else:
                        items.append(html.escape(item))
                else:
                    items.append(str(item))
            items_html = "\n".join(f"<li>{item}</li>" for item in items)
            return f"<ul>{items_html}</ul>"
        else:
            # If it's a string, render as text with links converted to <a> tags
            value_str = str(value)
            # Check if the value looks like a URL
            if is_external_url(value_str):
                return f'<a href="{html.escape(value_str)}">{html.escape(value_str)}</a>'
            else:
                return html.escape(value_str)

    def about(self):
        """
        Generates the "About" page based on default information.
        :return:
        """
        if not self._site_information:
            return "No site information has been set. Use the <code>set_site_information()</code> function to set the information about your site."

        # Build the about page content
        content_parts = []
        site_parts = [
            ("Author", self._site_information.author),
            ("Description", self._site_information.description),
            ("Sources", self._site_information.sources),
            ("Planning", self._site_information.planning),
            ("Links", self._site_information.links)
        ]

        for title, content in site_parts:
            if content:
                content_parts.append(f"<h2>{title}</h2>")
                content_parts.append(f"<div>{self.render_site_info(content)}</div>")

        # Add external pages if configured
        if self.configuration.external_pages:
            content_parts.append("<h2>External Pages</h2>")
            external_items = []
            # Parse semicolon-separated format: "URL Text;URL Text;..."
            for entry in self.configuration.external_pages.split(';'):
                entry = entry.strip()
                if not entry:
                    continue
                # Split on first whitespace to separate URL from optional label
                parts = entry.split(None, 1)
                if len(parts) == 2:
                    url, label = parts
                    external_items.append(f'<a href="{html.escape(url)}">{html.escape(label)}</a>')
                elif len(parts) == 1:
                    url = parts[0]
                    external_items.append(f'<a href="{html.escape(url)}">{html.escape(url)}</a>')
            if external_items:
                items_html = "\n".join(f"<li>{item}</li>" for item in external_items)
                content_parts.append(f"<ul>{items_html}</ul>")

        # Back button
        content_parts.append('<p><a href="/" class="btlw-back">← Back to the main page</a></p>')

        return "\n".join(content_parts)


    def setup(self, initial_state=None):
        """
        Initializes and configures the application. Sets up initial state, error
        pages, and application routes for handling requests.

        :param initial_state: The initial state to set up the application.
        :type initial_state: Any
        """
        self._state = initial_state
        self._initial_state = self.dump_state()
        self._initial_state_type = type(initial_state)
        self.app = Bottle()

        # Setup error pages
        def handle_404(error):
            """
            This is the default handler for HTTP 404 errors. It renders a custom error page
            that displays a message indicating the requested page was not found, and provides
            a link to return to the index page.
            """
            message = "<p>The requested page <code>{url}</code> was not found.</p>".format(url=request.url)
            # TODO: Only show if not the index
            message += "\n<p>You might want to return to the <a href='/'>index</a> page.</p>"
            original_error = f"{error.body}\n"
            if hasattr(error, 'traceback'):
                original_error += f"{error.traceback}\n"
            return TEMPLATE_404.format(title="404 Page not found", message=message,
                                       error=original_error,
                                       routes="\n".join(
                                           f"<li><code>{r!r}</code>: <code>{func}</code></li>" for r, func in
                                           self.original_routes))

        def handle_500(error):
            """
            This is the default handler for HTTP 500 errors. It renders a custom error page
            that displays a message indicating an internal server error occurred, and provides
            a link to return to the index page. along with some additional error details.
            """
            message = "<p>Sorry, the requested URL <code>{url}</code> caused an error.</p>".format(url=request.url)
            message += "\n<p>You might want to return to the <a href='/'>index</a> page.</p>"
            original_error = f"{error.body}\n"
            if hasattr(error, 'traceback'):
                original_error += f"{error.traceback}\n"
            return TEMPLATE_500.format(title="500 Internal Server Error",
                                       message=message,
                                       error=original_error,
                                       routes="\n".join(
                                           f"<li><code>{r!r}</code>: <code>{func}</code></li>" for r, func in
                                           self.original_routes))

        self.app.error(404)(handle_404)
        self.app.error(500)(handle_500)
        # Setup routes
        if not self.routes:
            raise ValueError("No routes have been defined.\nDid you remember the @route decorator?")
        self.app.route("/--reset", 'GET', self.reset)
        self.app.route("/--about", "GET", self.about)
        # If not skulpt, then allow them to test the deployment
        if not self.configuration.skulpt:
            self.app.route("/--test-deployment", 'GET', self.test_deployment)
        for url, func in self.routes.items():
            self.app.route(url, 'GET', func)
            self.app.route(url, "POST", func)
        if '/' not in self.routes:
            first_route = list(self.routes.values())[0]
            self.app.route('/', 'GET', first_route)
        self.handle_images()

    def run(self, **kwargs):
        """
        Executes the server application using the provided configuration. The method will
        update the configuration with any additional keyword arguments provided and start
        the server application with the updated configuration.

        :param kwargs: Arbitrary keyword arguments containing configuration updates. Only
            keys that match the ServerConfiguration fields will be applied.
        :return: None. The server application is started with the updated configuration.
        """
        final_args = asdict(self.configuration)
        # Update the configuration with the safe kwargs
        safe_keys = fields(ServerConfiguration)
        safe_key_names = {field.name for field in safe_keys}
        safe_kwargs = {key: value for key, value in kwargs.items() if key in safe_key_names}
        updated_configuration = replace(self.configuration, **safe_kwargs)
        self.configuration = updated_configuration
        # Update the final args with the new configuration
        final_args.update(kwargs)
        self.app.run(**final_args)

    def prepare_args(self, original_function, args, kwargs):
        """
        Processes and prepares arguments for the route function call, ensuring compatibility
        with expected parameters, handling state insertion, remapping parameters,
        and performing type conversion when necessary.

        :param original_function: The function whose parameters are being prepared.
        :param args: The positional arguments to be passed to the function.
        :param kwargs: The keyword arguments to be passed to the function.
        :return: A tuple containing:
            - Processed positional arguments matching the expected parameters of the
              function.
            - Processed keyword arguments matching the expected parameters of the
              function.
            - A string representation of the final arguments for logging or debugging.
            - The button pressed if detected and processed.
        """
        self._conversion_record.clear()
        args = list(args)
        kwargs = dict(**kwargs)
        button_pressed = ""
        params = get_params()
        if SUBMIT_BUTTON_KEY in params:
            button_pressed = json.loads(params.pop(SUBMIT_BUTTON_KEY))
        elif PREVIOUSLY_PRESSED_BUTTON in params:
            button_pressed = json.loads(params.pop(PREVIOUSLY_PRESSED_BUTTON))
        # TODO: Handle non-bottle backends
        param_keys = list(params.keys())
        for key in param_keys:
            kwargs[key] = params.pop(key)
        signature_parameters = inspect.signature(original_function).parameters
        expected_parameters = list(signature_parameters.keys())
        show_names = {param.name: (param.kind in (inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.VAR_KEYWORD))
                      for param in signature_parameters.values()}
        kwargs = remap_hidden_form_parameters(kwargs, button_pressed)
        # Insert state into the beginning of args
        if (expected_parameters and expected_parameters[0] == "state") or (
                len(expected_parameters) - 1 == len(args) + len(kwargs)):
            args.insert(0, self._state)
        # Check if there are too many arguments
        if len(expected_parameters) < len(args) + len(kwargs):
            self.flash_warning(
                f"The {original_function.__name__} function expected {len(expected_parameters)} parameters, but {len(args) + len(kwargs)} were provided.\n"
                f"  Expected: {', '.join(expected_parameters)}\n"
                f"  But got: {repr(args)} and {repr(kwargs)}")
            # TODO: Select parameters to keep more intelligently by inspecting names
            args = args[:len(expected_parameters)]
            while len(expected_parameters) < len(args) + len(kwargs) and kwargs:
                kwargs.pop(list(kwargs.keys())[-1])
        # Type conversion if required
        expected_types = {name: p.annotation for name, p in
                          inspect.signature(original_function).parameters.items()}
        args = [self.convert_parameter(param, val, expected_types)
                for param, val in zip(expected_parameters, args)]
        kwargs = {param: self.convert_parameter(param, val, expected_types)
                  for param, val in kwargs.items()}
        # Verify all arguments are in expected_parameters
        for key, value in kwargs.items():
            if key not in expected_parameters:
                raise ValueError(
                    f"Unexpected parameter {key}={value!r} in {original_function.__name__}. "
                    f"Expected parameters: {expected_parameters}")
        # Final return result
        representation = [safe_repr(arg) for arg in args] + [
            f"{key}={safe_repr(value)}" if show_names.get(key, False) else safe_repr(value)
            for key, value in sorted(kwargs.items(), key=lambda item: expected_parameters.index(item[0]))]
        return args, kwargs, ", ".join(representation), button_pressed

    def handle_images(self):
        """
        Handles the serving of images when the `deploy_image_path` is configured. This
        method maps a dynamic route to serve image files by their paths, allowing them
        to be accessed through the defined route.

        :raises AttributeError: If `self.configuration.deploy_image_path` or its
                                 attributes are not properly configured.
        :return: None
        """
        if self.configuration.deploy_image_path:
            self.app.route(f"/{self.configuration.deploy_image_path}/<path:path>", 'GET', self.serve_image)

    def serve_image(self, path):
        """
        Serves an image file located in the specified directory with the MIME type
        `image/png`. The method retrieves the image from the path provided, using
        the configured source image folder as the root directory.

        :param path: The relative path to the image file within the source image folder.
        :type path: str
        :return: The static file object representing the requested image.
        :rtype: static_file
        """
        return static_file(path, root='./' + self.configuration.src_image_folder, mimetype='image/png')

    def try_special_conversions(self, value, target_type):
        """
        Attempts to convert the input value to the specified target type using various
        specialized conversion methods. This method is designed to handle specific types
        of input, such as `bottle.FileUpload`, supporting conversion to bytes, string,
        dictionary, and, if available, `PIL.Image`.

        :param value: The input value to be converted. Typically, this is expected
            to be an instance of `bottle.FileUpload`.
        :type value: Any
        :param target_type: The desired type to convert the input value to. This can
            include types such as `bytes`, `str`, `dict`, or others, depending on the
            availability of appropriate conversion logic.
        :type target_type: type
        :return: The converted value as an instance of the specified target type.
            If no special conversion logic applies, the original value is passed
            to the target type directly for conversion.
        :rtype: Any
        :raises ValueError: If the method encounters an error during conversion,
            such as failure to decode file content as UTF-8, or if a file cannot be
            opened as an image using PIL.Image when `HAS_PILLOW` is `True`.
        """
        if isinstance(value, bottle.FileUpload):
            if target_type == bytes:
                return target_type(value.file.read())
            elif target_type == str:
                try:
                    return value.file.read().decode('utf-8')
                except UnicodeDecodeError as e:
                    raise ValueError(f"Could not decode file {value.filename} as utf-8. Perhaps the file is not the type that you expected, or the parameter type is inappropriate?") from e
            elif target_type == dict:
                return {'filename': value.filename, 'content': value.file.read()}
            elif HAS_PILLOW and issubclass(target_type, PILImage.Image):
                try:
                    image = PILImage.open(value.file)
                    image.filename = value.filename
                    return image
                except Exception as e:
                    # TODO: Allow configuration for just setting this to None instead, if there is an error
                    raise ValueError(f"Could not open image file {value.filename} as a PIL.Image. Perhaps the file is not an image, or the parameter type is inappropriate?") from e
        return target_type(value)

    def convert_parameter(self, param, val, expected_types):
        """
        Converts a given parameter value to a specified target type if possible, based
        on the expected types provided. Records successful conversions, unchanged
        parameters, and failed conversion attempts with detailed information.

        :param param: The name of the parameter to be converted.
        :type param: str
        :param val: The value of the parameter to be converted.
        :type val: Any
        :param expected_types: A dictionary containing the expected types for all
            parameters. The key is the parameter name, and the value is its expected
            type. If a parameter does not require conversion, its value is set to
            `inspect.Parameter.empty`.
        :type expected_types: dict
        :return: The converted value of the parameter if a conversion is successful;
            otherwise, the original value of the parameter.
        :rtype: Any
        :raises ValueError: If the value cannot be converted to its specified expected
            type, providing detailed information about the attempted conversion.
        """
        if param in expected_types:
            expected_type = expected_types[param]
            if expected_type == inspect.Parameter.empty:
                self._conversion_record.append(UnchangedRecord(param, val, expected_types[param]))
                return val
            if hasattr(expected_type, '__origin__'):
                # TODO: Ignoring the element type for now, but should really handle that properly
                expected_type = expected_type.__origin__
            if not isinstance(val, expected_type):
                try:
                    target_type = expected_types[param]
                    converted_arg = self.try_special_conversions(val, target_type)
                    self._conversion_record.append(ConversionRecord(param, val, expected_types[param], converted_arg))
                except Exception as e:
                    try:
                        from_name = type(val).__name__
                        to_name = expected_types[param].__name__
                    except:
                        from_name = repr(type(val))
                        to_name = repr(expected_types[param])
                    raise ValueError(
                        f"Could not convert {param} ({val!r}) from {from_name} to {to_name}\n") from e
                return converted_arg
        # Fall through
        self._conversion_record.append(UnchangedRecord(param, val))
        return val

    def make_bottle_page(self, original_function):
        """
        A decorator that wraps a given function to create and manage a Bottle web
        page environment. This includes processing request parameters, building
        the page, verifying its content, and rendering it to the client. It also
        maintains state and history for the page creation and execution process.

        :param original_function: The original callable function to be wrapped
            and executed to construct the page.
        :return: A wrapped function that, when called, executes the original
            function within the Bottle page handling logic.
        """
        @wraps(original_function)
        def bottle_page(*args, **kwargs):
            # TODO: Handle non-bottle backends
            url = remove_url_query_params(request.url, {RESTORABLE_STATE_KEY, SUBMIT_BUTTON_KEY})
            self.restore_state_if_available(original_function)
            original_state = self.dump_state()
            try:
                args, kwargs, arguments, button_pressed = self.prepare_args(original_function, args, kwargs)
            except Exception as e:
                return self.make_error_page("Error preparing arguments for page", e, original_function)
            # Actually start building up the page
            visiting_page = VisitedPage(url, original_function, arguments, "Creating Page", button_pressed)
            self._page_history.append((visiting_page, original_state))
            try:
                page = original_function(*args, **kwargs)
            except Exception as e:
                additional_details = (f"  Arguments: {args!r}\n"
                                      f"  Keyword Arguments: {kwargs!r}\n"
                                      f"  Button Pressed: {button_pressed!r}\n"
                                      f"  Function Signature: {inspect.signature(original_function)}")
                return self.make_error_page("Error creating page", e, original_function, additional_details)
            visiting_page.update("Verifying Page Result", original_page_content=page)
            verification_status = self.verify_page_result(page, original_function)
            if verification_status:
                return verification_status
            try:
                page.verify_content(self)
            except Exception as e:
                return self.make_error_page("Error verifying content", e, original_function)
            self._state_history.append(page.state)
            self._state = page.state
            visiting_page.update("Rendering Page Content")
            try:
                content = page.render_content(self.dump_state(), self.configuration)
            except Exception as e:
                return self.make_error_page("Error rendering content", e, original_function)
            visiting_page.finish("Finished Page Load")
            if self.configuration.debug:
                content = content + self.make_debug_page()
            content = self.wrap_page(content)
            return content

        return bottle_page

    def verify_page_result(self, page, original_function):
        """
        Verifies the result of a function execution to ensure it returns a valid `Page`
        object. The verification checks whether the returned result is of type `Page`
        and whether its structure adheres to the expected format. If the validation
        fails, an error message is generated and returned.

        :param page: The object returned by the endpoint method to be verified.
        :type page: Union[None, str, list, Any]
        :param original_function: A reference to the function or method where the
            `Page` object is expected to be returned from.
        :type original_function: Callable
        :return: Returns either a valid `Page` object or an error page with diagnostic
            information when the verification process fails.
        :rtype: Optional[Page]
        """
        message = ""
        if page is None:
            message = (f"The server did not return a Page object from {original_function}.\n"
                       f"Instead, it returned None (which happens by default when you do not return anything else).\n"
                       f"Make sure you have a proper return statement for every branch!")
        elif isinstance(page, str):
            message = (
                f"The server did not return a Page() object from {original_function}. Instead, it returned a string:\n"
                f"  {page!r}\n"
                f"Make sure you are returning a Page object with the new state and a list of strings!")
        elif isinstance(page, list):
            message = (
                f"The server did not return a Page() object from {original_function}. Instead, it returned a list:\n"
                f" {page!r}\n"
                f"Make sure you return a Page object with the new state and the list of strings, not just the list of strings.")
        elif not isinstance(page, Page):
            message = (f"The server did not return a Page() object from {original_function}. Instead, it returned:\n"
                       f" {page!r}\n"
                       f"Make sure you return a Page object with the new state and the list of strings.")
        else:
            verification_status = self.verify_page_state_history(page, original_function)
            if verification_status:
                return verification_status
            elif isinstance(page.content, str):
                message = (f"The server did not return a valid Page() object from {original_function}.\n"
                           f"Instead of a list of strings or content objects, the content field was a string:\n"
                           f" {page.content!r}\n"
                           f"Make sure you return a Page object with the new state and the list of strings/content objects.")
            elif not isinstance(page.content, list):
                message = (
                    f"The server did not return a valid Page() object from {original_function}.\n"
                    f"Instead of a list of strings or content objects, the content field was:\n"
                    f" {page.content!r}\n"
                    f"Make sure you return a Page object with the new state and the list of strings/content objects.")
            else:
                for item in page.content:
                    if not isinstance(item, (str, PageContent)):
                        message = (
                            f"The server did not return a valid Page() object from {original_function}.\n"
                            f"Instead of a list of strings or content objects, the content field was:\n"
                            f" {page.content!r}\n"
                            f"One of those items is not a string or a content object. Instead, it was:\n"
                            f" {item!r}\n"
                            f"Make sure you return a Page object with the new state and the list of strings/content objects.")

        if message:
            return self.make_error_page("Error after creating page", ValueError(message), original_function)

    def verify_page_state_history(self, page, original_function):
        """
        Validates the consistency of the state object's type in the provided `page`
        against the most recent state stored in the `self._state_history`. If any
        discrepancy is found in the type of the state object, it constructs an error
        message highlighting the inconsistency and generates an error page.

        :param page: The page object containing the state to be verified.
        :param original_function: The name of the function that created the page.
        :return: Returns an error page if a validation issue arises, otherwise none.
        """
        if not self._state_history:
            return
        message = ""
        last_type = self._state_history[-1].__class__
        if not isinstance(page.state, last_type):
            message = (
                f"The server did not return a valid Page() object from {original_function}. The state object's type changed from its previous type. The new value is:\n"
                f" {page.state!r}\n"
                f"The most recent value was:\n"
                f" {self._state_history[-1]!r}\n"
                f"The expected type was:\n"
                f" {last_type}\n"
                f"Make sure you return the same type each time.")
        # TODO: Typecheck each field
        if message:
            return self.make_error_page("Error after creating page", ValueError(message), original_function)

    def wrap_page(self, content):
        """
        Wraps provided content in a styled HTML template, applying additional headers,
        scripts, styles, and any configuration-specific content.

        :param content: The content to be wrapped in the HTML template.
        :type content: str

        :raises ValueError: If the specified style in the configuration is not found
            in the list of included styles.

        :return: A fully formatted HTML string, including necessary headers, styles,
            scripts, and the provided content wrapped according to the configuration
            and selected style.
        :rtype: str
        """
        content = f"<div class='btlw'>{content}</div>"
        style = self.configuration.style
        global_files = get_raw_files("global")
        style_files = get_raw_files(style)
        if style_files is None:
            possible_themes = ", ".join(get_themes())
            raise ValueError(f"Unknown style {style}. Please choose from {possible_themes}, or add a custom style tag with add_website_header.")

        scripts = "\n".join([*global_files.scripts.values(), *style_files.scripts.values()])
        styles = "\n".join([*global_files.styles.values(), *style_files.styles.values()])
        credit = "\n".join(c for c in [
            style_files.metadata.get('credit', ''),
            global_files.metadata.get('credit', ''),
        ] if c)
        if self.configuration.additional_header_content:
            header_content = "\n".join(self.configuration.additional_header_content)
        else:
            header_content = ""
        if self.configuration.additional_css_content:
            additional_css = "\n".join(self.configuration.additional_css_content)
            styles = f"{styles}\n<style>{additional_css}</style>"
        if self.configuration.skulpt:
            return TEMPLATE_200_WITHOUT_HEADER.format(
                header=header_content, styles=styles, scripts=scripts, content=content,
                title=json.dumps(self.configuration.title))
        else:
            return TEMPLATE_200.format(
                header=header_content, styles=styles, scripts=scripts, content=content,
                title=html.escape(self.configuration.title),
                credit=credit)


    def make_error_page(self, title, error, original_function, additional_details=""):
        """
        Generates and displays a detailed error page upon encountering an issue in the application.

        This function formats a detailed error message by including the title of the error,
        the original function's name where the error occurred, the original error's message, and
        any additional details if provided. It also escapes potentially unsafe HTML characters
        from the error details and traceback to improve security. The formatted message is then
        displayed with an HTTP 500 Internal Server Error status.

        :param title: A brief, descriptive title for the error (e.g., "Server Error").
        :type title: str
        :param error: The original error/exception that was encountered.
        :type error: Exception
        :param original_function: The function object where the error originated.
        :type original_function: Callable
        :param additional_details: Optional additional information or context about the error. Defaults to an empty string.
        :type additional_details: str
        :return: Does not return any value as it raises an HTTP 500 error with the formatted message.
        :rtype: None
        """
        tb = html.escape(traceback.format_exc())
        new_message = (f"""{title}.\n"""
                       f"""Error in {original_function.__name__}:\n"""
                       f"""{html.escape(str(error))}\n\n\n{tb}""")
        if additional_details:
            new_message += f"\n\n\nAdditional Details:\n{additional_details}"
        abort(500, new_message)

    def flash_warning(self, message):
        """
        This method displays a warning message. It is intended for immediate
        output to notify the user of a specific warning or issue.

        TODO: This should actually append to a list that gets shown in the debug area.

        :param message: The warning message to be displayed to the user.
        :type message: str
        :return: None
        """
        print(message)

    def make_debug_page(self):
        """
        Generates a debug page by gathering and processing various internal states and
        informational data.

        This method collects the page history, current state, routes, configuration,
        and conversion record to create a representation of a debug page. It utilizes
        these components to generate a structured output that represents the debug
        information.

        :return: Debug information page content generated based on the current internal
                 state and history of the application.
        :rtype: str
        """
        content = DebugInformation(self._page_history, self._state, self.routes, self._conversion_record,
                                   self.configuration)
        return content.generate()

    def test_deployment(self):
        """
        Bundles files necessary for deployment, including the source code identified by
        the "start_server" line in the student's main file. This allows the server to
        "deploy" a local version of the application, as it would appear on a live server
        using Skulpt.

        This function searches for the entry point of the student's application and
        attempts to bundle it with all its associated files into a deployable format.
        If the main file cannot be located, it returns an error indicating the failure
        to find the required file. Otherwise, it creates a bundled JavaScript version
        of the required files and integrates them with the appropriate configurations
        for deployment.

        :raises ValueError: If the student's main file cannot be located.

        :raises IOError: If there are issues during the file bundling process.

        :return: HTML template string formatted with bundled JavaScript and CDN
                 configurations.
        :rtype: str
        """
        # Bundle up the necessary files, including the source code
        student_main_file = seek_file_by_line("start_server")
        if student_main_file is None:
            return TEMPLATE_500.format(title="500 Internal Server Error",
                                       message="Could not find the student's main file.",
                                       error="Could not find the student's main file.",
                                       routes="")
        bundled_js, skipped, added = bundle_files_into_js(student_main_file, os.path.dirname(student_main_file))
        bundled_js = protect_script_tags(bundled_js)
        drafter_setup_code = "\n".join(get_raw_files('global').deploy.values())
        return TEMPLATE_SKULPT_DEPLOY.format(website_code=bundled_js,
                                             cdn_skulpt=self.configuration.cdn_skulpt,
                                             cdn_skulpt_std=self.configuration.cdn_skulpt_std,
                                             cdn_skulpt_drafter=self.configuration.cdn_skulpt_drafter,
                                             website_setup=drafter_setup_code)

MAIN_SERVER = Server(_custom_name="MAIN_SERVER")

def set_main_server(server: Server):
    """
    Sets the main server to the given server. This is useful for testing purposes.

    :param server: The server to set as the main server
    :return: None
    """
    global MAIN_SERVER
    MAIN_SERVER = server

def get_main_server() -> Server:
    """
    Gets the main server. This is useful for testing purposes.

    :return: The main server
    """
    return MAIN_SERVER

def get_all_routes(server: Optional[Server] = None):
    """
    Get all routes available in the given server or the main server if none is provided.

    If the `server` parameter is not specified, the function retrieves the main server
    using the `get_main_server()` function and returns its list of routes.

    :param server: An optional `Server` instance. If provided, the method will retrieve
        routes specific to this server. If omitted, it defaults to the main server.
    :type server: Optional[Server]

    :return: Returns a list of routes from the provided or default main server.
    """
    if server is None:
        server = get_main_server()
    return server.routes


def get_server_setting(key, default=None, server=MAIN_SERVER):
    """
    Gets a setting from the server's configuration. If the setting is not found, the default value is returned.

    :param key: The key to look up in the configuration
    :param default: The default value to return if the key is not found
    :param server: The server to look up the setting in (defaults to the ``MAIN_SERVER``)
    :return: The value of the setting, or the default value if not found
    """
    return getattr(server.configuration, key, default)


def start_server(initial_state=None, server: Server = MAIN_SERVER, skip=False, **kwargs):
    """
    Starts the server with the given initial state and configuration. If the server is set to skip, it will not start.
    Additional keyword arguments will be passed to the server's run method, and therefore to Bottle. This can be
    used to control things like the ``port``.

    :param initial_state: The initial state to start the server with
    :param server: The server to run on, defaulting to ``MAIN_SERVER``
    :param skip: If True, the server will not start; this is useful for running tests headlessly
    :param kwargs: Additional keyword arguments to pass to the server's run method. See below.
    :return: None

    :Keyword Arguments:
        * *port* (``int``) --
          The port to run the server on. Defaults to ``8080``
    """
    if server.configuration.must_have_site_information:
        if not server._site_information:
            raise ValueError("You must set the site information before starting the server. Use set_site_information().")
    if server.configuration.skip or skip:
        logger.info("Skipping server setup and execution")
        return
    server.setup(initial_state)
    server.run(**kwargs)
