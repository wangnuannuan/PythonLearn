from __future__ import print_function, division, absolute_import, unicode_literals
import os
from embarc_tools.project import Generator
from embarc_tools.settings import get_input
from embarc_tools.notify import print_string
from ..download_manager import cd
from ..osp import (osp)
help = "Ide generator"


def run(args):
    buildopts = dict()
    osppath = osp.OSP()
    path = None
    if args.board:
        buildopts["BOARD"] = args.board
    if args.bd_ver:
        buildopts["BD_VER"] = args.bd_ver
    if args.cur_core:
        buildopts["CUR_CORE"] = args.cur_core
    if args.toolchain:
        buildopts["TOOLCHAIN"] = args.toolchain
    if args.project:
        path = args.project
    else:
        path = os.getcwd()

    if os.path.exists(path):
        makefile = osppath.get_makefile(path)
        if not makefile:
            msg = "This is not a valid application path"
            print_string(msg, level="error")
            return
        with cd(path):
            if os.path.exists(".project") and os.path.exists(".cproject"):
                while True:
                    yes = get_input("The IDE project already exists, recreate and overwrite the old files [Y/N]  ")
                    if yes in ["yes", "Y", "y"]:
                        break
                    elif yes in ["no", "n", "N"]:
                        return
                    else:
                        continue

            if args.generate:
                generator = Generator()
                for project in generator.generate(buildopts=buildopts):
                    project.generate()


def setup(subparser):
    subparser.add_argument(
        "-g", "--generate", action="store_true", help="Application to be created")
    subparser.add_argument(
        "-p", "--project", help="Application path")
    subparser.add_argument(
        "-b", "--board", help="Update build configuration: board")
    subparser.add_argument(
        "--bd_ver", help="Update build configuration: board version")
    subparser.add_argument(
        "--cur_core", help="Update build configuration: core")
    subparser.add_argument(
        "--toolchain", help="Update build configuration: toolchain")
