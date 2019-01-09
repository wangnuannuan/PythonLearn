from __future__ import print_function, absolute_import, unicode_literals, unicode_literals
import os
import collections
from embarc_tools.settings import get_input, SUPPORT_TOOLCHAIN
from embarc_tools.notify import (print_string, print_table)
from embarc_tools.exporter import Exporter
from embarc_tools.settings import BUILD_CONFIG_TEMPLATE
from ..osp import osp
from ..download_manager import mkdir, getcwd

help = "Create a new application"


def run(args, remainder=None):

    olevel = args.olevel
    application = args.application

    if not application:
        while True:
            application = get_input("[embARC] Input application name: ")
            if application == "":
                print_string("Please don't set applcation name as a empty string ")
                application = None
                continue
            else:
                break
    args.application = application
    config = build_config(args)
    # config["APPL"] = application
    print_string("Current configuration ")
    table_head = list()
    table_content = list()
    for key, value in config.items():
        table_head.append(key)
        table_content.append(value)
    print_table([table_head, [table_content]])

    config["olevel"] = olevel
    app_path = os.path.join(getcwd(), application)
    config["EMBARC_OSP_ROOT"] = config["EMBARC_OSP_ROOT"].replace("\\", "/")
    config["middleware"] = args.middleware
    config["csrc"] = args.csrc
    config["asmsrc"] = args.asmsrc
    config["include"] = args.include
    config["defines"] = args.defines
    config["os"] = args.os
    config["lib"] = args.library
    print_string("Start to generate makefile and main.c ")
    exporter = Exporter("application")
    exporter.gen_file_jinja("makefile.tmpl", config, "makefile", application)
    exporter.gen_file_jinja("main.c.tmpl", config, "main.c", application)
    print_string("Finish generate makefile and main.c, and they are in " + app_path)
    print(args.csrc)
    if args.csrc != ".":
        mkdir(os.path.join(getcwd(), application, args.csrc))


def build_config(args):
    osppath = osp.OSP()
    osppath.list_path()
    input_root = args.osp_root
    if not input_root:
        input_root = get_input("[embARC] Choose osp root or set another path as osp root: ")
    board = args.board
    bd_ver = args.bd_ver
    cur_core = args.cur_core
    toolchain = args.toolchain
    # config = dict()
    config = BUILD_CONFIG_TEMPLATE
    config["EMBARC_OSP_ROOT"] = str()
    config = collections.OrderedDict()
    config["APPL"] = args.application
    osp_root = osppath.is_osp(input_root)

    if not osp_root:
        msg = "What you choose is not a valid osp root"
        print_string(msg, level="warning")

        osp_root = osppath.get_path()
        if osp_root:
            print_string("Here choose " + osp_root + "as osp root")
        else:
            osppath.clear_path()
            print_string("Please set a valid osp root or download embarc osp first")
            return None
    print_string("Current osp root is: " + osp_root)

    support_board = osppath.support_board(osp_root)
    print_string("Support board : {}".format("  ".join(support_board)))
    while True:
        if not board:
            board = get_input("[embARC] Choose board: ")
        if board not in support_board:
            board = None
            print_string("Please choose board from {}" .format(support_board))
            continue
        else:
            break
    config["BOARD"] = board
    support_bd_ver = osppath.get_board_version(osp_root, board)
    print_string("{} support versions : {}".format(board, "  ".join(support_bd_ver)))
    while True:
        if not bd_ver:
            bd_ver = get_input("[embARC] Choose board version: ")
        if bd_ver not in support_bd_ver:
            bd_ver = None
            print_string("Please choose version from {}" .format(support_bd_ver))
            continue
        else:
            break
    config["BD_VER"] = bd_ver

    support_core = osppath.get_tcfs(osp_root, board, bd_ver)
    print_string("{} with versions {} support cores : {}".format(board, bd_ver, "  ".join(support_core)))
    while True:
        if not cur_core:
            cur_core = get_input("[embARC] choose core: ")
        if cur_core not in support_core:
            cur_core = None
            print_string("Please choose core from {}" .format(support_core))
            continue
        else:
            break
    config["CUR_CORE"] = cur_core
    support_toolchains = SUPPORT_TOOLCHAIN
    print_string("Support toolchains: {}".format("  ".join(support_toolchains)))
    while True:
        if not toolchain:
            toolchain = get_input("[embARC] Choose toolchain: ")
        if toolchain not in support_toolchains:
            toolchain = None
            print_string("Please choose toolchain from {}" .format(support_toolchains))
            continue
        else:
            break
    config["TOOLCHAIN"] = toolchain
    config["EMBARC_OSP_ROOT"] = os.path.abspath(osp_root)
    return config


def setup(subparser):
    subparser.add_argument(
        "-a", "--application", help="Application to be created")
    subparser.add_argument(
        "-b", "--board", help="Choose board")
    subparser.add_argument(
        "--bd_ver", help="Choose board version")
    subparser.add_argument(
        "--cur_core", help="Choose core")
    subparser.add_argument(
        "--toolchain", help="Choose toolchain")
    subparser.add_argument(
        "--osp_root", help="Choose embARC osp root path")
    subparser.add_argument(
        "-o", "--olevel", default="O3", help="Choose olevel")
    subparser.add_argument(
        '-m', '--middleware', action='store', default="common", help='Choose a middleware')
    subparser.add_argument(
        '--csrc', action='store', default=".", help='Application source dirs')
    subparser.add_argument(
        '--asmsrc', action='store', default=".", help='Application source dirs')
    subparser.add_argument(
        '--include', action='store', default=".", help='Application include dirs')
    subparser.add_argument(
        '--defines', action='store', default=".", help='Application defines')
    subparser.add_argument(
        '--os', action='store', default="", help='Choose os')
    subparser.add_argument(
        '--library', action='store', default="", help='Choose library')
