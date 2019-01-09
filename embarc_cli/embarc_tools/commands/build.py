from __future__ import print_function, division, absolute_import, unicode_literals
import os
from ..builder import build
from ..download_manager import cd, generate_file
help = "Build application"


def run(args, remainder=None):
    buildopts = dict()
    osproot = None
    curdir = args.outdir
    app_path = None
    recordBuildConfig = None
    if args.path:
        app_path = args.path

    if os.path.exists(app_path) and os.path.isdir(app_path):
        with cd(app_path):
            if os.path.exists(".build"):
                with open(".build", "r") as f:
                    content = f.read().splitlines()
                    if len(content) > 0:
                        recordBuildConfig = (content[0]).split()
    if recordBuildConfig is not None:
        for recoreOpt in recordBuildConfig:
            if "=" in recoreOpt:
                opt, value = recoreOpt.split("=")
                if opt in build.BUILD_OPTION_NAMES:
                    buildopts[opt] = recoreOpt.split("=")[1]

    parallel = args.parallel
    if args.board:
        buildopts["BOARD"] = args.board
    if args.bd_ver:
        buildopts["BD_VER"] = args.bd_ver
    if args.core:
        buildopts["CUR_CORE"] = args.core
    if args.toolchain:
        buildopts["TOOLCHAIN"] = args.toolchain

    builder = build.embARC_Builder(osproot, buildopts, curdir)

    if remainder:
        make_config, target= get_config(remainder)
        if target:
            args.target = target

        current_options = builder.buildopts
        current_options.update(make_config)
        make_config_update = list()
        for key, value in current_options.items():
            option = "%s=%s" % (key, value)
            make_config_update.append(option)
        builder.make_options = " ".join(make_config_update)
    if args.target:
        information = None
        if args.target == "elf":
            information = builder.build_elf(app_path, parallel=parallel, pre_clean=False, post_clean=False)
        elif args.target == "bin":
            information = builder.build_bin(app_path, parallel=parallel, pre_clean=False, post_clean=False)
        elif args.target == "hex":
            information = builder.build_hex(app_path, parallel=parallel, pre_clean=False, post_clean=False)
        elif args.target == "clean":
            information = builder.clean(app_path)
        elif args.target == "distclean":
            information = builder.distclean(app_path)
        elif args.target == "boardclean":
            information = builder.boardclean(app_path)
        elif args.target == "info":
            information = builder.get_build_info(app_path)
        elif args.target == "size":
            information = builder.get_build_size(app_path)
        elif args.target:
            information = builder.build_target(app_path, target=args.target, parallel=False, coverity=False)
        else:
            print("[embARC] Please choose right target")
        if information["result"]:
            generate_file(".build", information["build_cmd"], path=app_path)


def get_config(config):
    make_config = dict()
    target = None
    if config:
        for key in config:
            if "=" in key:
                config_pair = key.split("=")
                make_config[config_pair[0]] = config_pair[1]
            else:
                target = key
    return make_config, target


def setup(subparser):
    subparser.add_argument(
        "-d", "--path", default=".", help="Application path")
    subparser.add_argument(
        "--outdir", help="Copy all files to this exported directory")
    subparser.add_argument(
        "-b", "--board", help="Build using the given BOARD")
    subparser.add_argument(
        "--bd_ver", help="Build using the given BOARD VERSION")
    subparser.add_argument(
        "--core", help="Build using the given CORE")
    subparser.add_argument(
        "--toolchain", help="Build using the given TOOLCHAIN")
    subparser.add_argument(
        "-j", "--parallel", default=False, help="Build application with -j")
    subparser.add_argument(
        "--target", default="elf", help="Choose build target, default target is elf and options are [elf, bin, hex, size] ")
