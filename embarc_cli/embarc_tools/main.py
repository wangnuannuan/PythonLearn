from __future__ import print_function, absolute_import, unicode_literals
import argparse
import sys
import pkgutil
import importlib
import pkg_resources
from embarc_tools import commands


def import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    results = {}
    for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


SUBCOMMANDS = import_submodules(commands)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', dest='verbosity', action='count', default=0,
        help='Increase the verbosity of the output'
    )
    parser.add_argument(
        '-q', dest='quietness', action='count', default=0,
        help='Decrease the verbosity of the output'
    )
    parser.add_argument(
        "--version", action='version',
        version=pkg_resources.require("embarc_cli")[0].version,
        help="Display version"
    )
    subparsers = parser.add_subparsers(help='commands')

    for name, module in SUBCOMMANDS.items():
        subparser = subparsers.add_parser(name, help=module.help)

        module.setup(subparser)
        subparser.set_defaults(func=module.run)
    args = None
    argv_list = list()
    if len(sys.argv) == 1:
        return parser.print_help()

    args, remainder = parser.parse_known_args()
    return args.func(args, remainder)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt):
        print("Terminate batch job")
