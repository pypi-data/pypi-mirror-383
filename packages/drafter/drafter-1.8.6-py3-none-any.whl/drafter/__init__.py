from drafter.setup import *
from drafter.components import *
from drafter.styling import *
from drafter.routes import *
from drafter.server import *
from drafter.deploy import *
from drafter.testing import assert_equal
import drafter.hacks

# Provide default route
route('index')(default_index)

__version__ = '1.8.6'

if __name__ == '__main__':
    import sys
    from drafter.command_line import parse_args, build_site
    # print("This package is meant to be imported, not run as a script. For now, at least.")
    options = parse_args(sys.argv[1:])
    build_site(options)