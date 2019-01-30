from __future__ import print_function, division, absolute_import, unicode_literals
import os
import collections
from embarc_tools.settings import SUPPORT_TOOLCHAIN, OLEVEL
from embarc_tools.notify import print_string, print_table
from ..download_manager import getcwd, read_json, generate_json
from ..osp import osp

help = "Get or set application config"
description = ("Show detail config.\n"
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
        defaultBuildConfig = collections.OrderedDict()
        _, defaultBuildConfig = osppath.get_makefile_config(defaultBuildConfig)
        if os.path.exists(embarc_config):
            print_string("Read embarc_config.json")
            recordConfig = read_json(embarc_config)
            defaultBuildConfig.update(recordConfig)

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
        "-a", "--application", help="Specify the path of the application")
    subparser.add_argument(
        "-b", "--board", help="Set board")
    subparser.add_argument(
        "--bd_ver", help="Set board version")
    subparser.add_argument(
        "--cur_core", help="Set core")
    subparser.add_argument(
        "--toolchain", help="Set toolchain")
    subparser.add_argument(
        "--osp_root", help="Set embARC osp root path")
    subparser.add_argument(
        "-o", "--olevel", help="Set olevel")
