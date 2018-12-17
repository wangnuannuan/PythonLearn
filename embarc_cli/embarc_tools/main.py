from __future__ import print_function, absolute_import, unicode_literals
import argparse
import os
import sys
import pkg_resources
from embarc_tools import commands
import pkgutil
import importlib


def import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


subcommands = import_submodules(commands)


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

    for name, module in subcommands.items():
        subparser = subparsers.add_parser(name, help=module.help)

        module.setup(subparser)
        subparser.set_defaults(func=module.run)
    args = None
    argv_list = list()
    if len(sys.argv) == 1:
        return parser.print_help()

    elif len(sys.argv) > 1 and sys.argv[1] == "build":
        argv_list.append(sys.argv[1])
        make_list = list()
        end_index = 0
        target = None
        j = 0
        sys.argv[1:]
        for argv in sys.argv[2:]:
            j += 1
            distance = (j - end_index)
            if "=" in argv:
                end_index = j
                make_list.append(argv)
            elif distance == 1:
                if "-" not in argv:
                    target = argv
                else:
                    argv_list.append(argv)
            else:
                argv_list.append(argv)
        if len(make_list) > 0:
            make_config = " ".join(make_list)
            argv_list.extend(["--make", make_config])
        if target:
            argv_list.extend(["--target", target])
        args = parser.parse_args(argv_list)
    else:
        args = parser.parse_args()

    verbosity = args.verbosity - args.quietness
    return args.func(args)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt):
        print("Terminate batch job")
