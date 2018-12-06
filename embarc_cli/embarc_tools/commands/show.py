from __future__ import print_function, division, absolute_import, unicode_literals
from embarc_tools.settings import *
from ..osp import (osp)
from ..notify import (print_string, print_table)

help = "Build configurations in embarc osp"

def run(args):
    osp_root = args.osp
    osppath = osp.OSP()
    if not any([args.board, args.bd_ver, args.core, args.toolchain, args.middleware,args.libraries]):
        msg = "Please select a parameter [--board --bd_ver --core --toolchain --middleware --libraries]"
        print_string(msg, level="warning")
        return
    if osp_root:
        if not osppath.is_osp(osp_root):
            osp_root = osppath.get_path()
    if osp_root:
        show = False
        print_string("Here choose " + osp_root + "as osp root")
        if args.board:

            support_board = osppath.support_board(osp_root)
            print_string("Support board : {}".format("  ".join(support_board)))
        if args.bd_ver:
            print_string("Support board version")
            table_head = ["board", "version"]
            table_content = list()
            support_board = osppath.support_board(osp_root)
            for board in support_board:
                bd_ver = osppath.get_board_version(osp_root, board)
                version = " ".join(bd_ver)
                table_content.append([board, version])

            print_table([table_head, table_content])
        if args.core:
            print_string("Support cores")
            table_head = ["board", "version", "cores"]
            table_content = list()
            support_board = osppath.support_board(osp_root)
            for board in support_board:
                bd_ver = osppath.get_board_version(osp_root, board)
                for bd_version in bd_ver:
                    cur_core = osppath.get_tcfs(osp_root, board, bd_version)
                    cores = " ".join(cur_core)
                    table_content.append([board, bd_version, cores])
            print_table([table_head, table_content])
        if args.toolchain:
            print_string("Support toolchain : {}".format("  ".join(SUPPORT_TOOLCHAIN)))
        if args.middleware:
            print_string("Support middleware : {}".format("  ".join(MIDDLEWARE)))
        if args.libraries:
            print_string("Support libraries : {}".format("  ".join(LIBRARIES)))

    else:
        msg = "Please set a valid osp root [--osp]"
        print_string(msg, level="warning")

def setup(subparser):
    subparser.add_argument(
        "--osp", default=".", help="Choose a osp root to get configurations")
    subparser.add_argument(
        "--board", action="store_true", help="List support boards")
    subparser.add_argument(
        "--bd_ver", action="store_true", help="List support board versions")
    subparser.add_argument(
        "--core", action="store_true", help="List support cores")
    subparser.add_argument(
        "--toolchain", action="store_true", help="List support toolchains")
    subparser.add_argument(
        "--middleware", action="store_true", help="List support middlewares")
    subparser.add_argument(
        "--libraries", action="store_true", help="List support libraries")
