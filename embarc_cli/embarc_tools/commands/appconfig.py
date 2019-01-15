from __future__ import print_function, division, absolute_import, unicode_literals
import os
from embarc_tools.settings import SUPPORT_TOOLCHAIN, OLEVEL
from embarc_tools.utils import pquery
from embarc_tools.notify import print_string, print_table
from ..download_manager import getcwd, cd, read_json, generate_json, mkdir
from ..osp import osp
from ..builder import build
help = "Get or set application config"
description = (
        "Show detail config.\n"
        "Currently supported options: board, board verion, ccurrent core, toolchain, olevel and embarc root.\n"
        "Result is to look for embarc_app.json, default options in makefile will be overridden by it")

def run(args, remainder=None):
    root = getcwd()
    app_path = None
    osppath = osp.OSP()

    if not args.application:
        app_path = root
    else:
        app_path = os.path.join(root, args.application)
    osppath = osp.OSP()
    makefile = osppath.get_makefile(app_path)
    if makefile:
        embarc_config = os.path.join(app_path, "embarc_app.json")
        defaultBuildConfig = dict()
        if os.path.exists(embarc_config):
            defaultBuildConfig = read_json(embarc_config)
        if args.osp_root:
            osp_root, _ = osppath.check_osp(args.osp_root)
            defaultBuildConfig["EMBARC_OSP_ROOT"] = osp_root.replace("\\", "/")

        if args.board:
            defaultBuildConfig["BOARD"] = args.board
        if args.bd_ver:
            defaultBuildConfig["BD_VER"] = args.bd_ver
        if args.cur_core:
            defaultBuildConfig["CUR_CORE"] = args.cur_core
        if args.toolchain and args.toolchain in SUPPORT_TOOLCHAIN:
            defaultBuildConfig["TOOLCHAIN"] = args.toolchain
        if args.olevel and args.olevel in OLEVEL:
            defaultBuildConfig["OLEVEL"] = args.olevel
            
        if args.middleware:
            defaultBuildConfig["MIDDLEWARE"] = args.middleware
        if args.csrc:
            defaultBuildConfig["APPL_CSRC_DIR"] = args.csrc
            mkdir(os.path.join(app_path, args.csrc))
        if args.asmsrc:
            defaultBuildConfig["APPL_ASMSRC_DIR"] = args.asmsrc
        if args.include:
            defaultBuildConfig["APPL_INC_DIR"] = args.include
        if args.defines:
            defaultBuildConfig["APPL_DEFINES"] = args.defines
        if args.os:
            defaultBuildConfig["OS_SEL"] = args.os
        if args.library:
            defaultBuildConfig["LIB_SEL"] = args.library

        generate_json(defaultBuildConfig, embarc_config)
        print_string("Current configuraion")
        table_head = ["option", "value"]
        table_content = [[key, value] for key, value in defaultBuildConfig.items()]
        msg = [table_head]
        msg.append(table_content)
        print_table(msg)



    else:
        print_string("[embARC] Please set a valid application path")
        return 


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
        "-o", "--olevel", help="Choose olevel")
    subparser.add_argument(
        '-m', '--middleware', action='store', help='Choose a middleware')
    subparser.add_argument(
        '--csrc', action='store', help='Application source dirs')
    subparser.add_argument(
        '--asmsrc', action='store', help='Application source dirs')
    subparser.add_argument(
        '--include', action='store', help='Application include dirs')
    subparser.add_argument(
        '--defines', action='store', help='Application defines')
    subparser.add_argument(
        '--os', action='store', help='Choose os')
    subparser.add_argument(
        '--library', action='store', help='Choose library')
