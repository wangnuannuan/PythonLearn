from __future__ import print_function, division, absolute_import, unicode_literals
from embarc_tools.notify import print_string
from ..toolchain import gnu, metaware
help = "Download and install toolchain(gnu)"


def run(args, remainder=None):
    toolchain_class = None
    if args.toolchain == "gnu":
        toolchain_class = gnu.Gnu()
    elif args.toolchain == "mw":
        toolchain_class = metaware.Mw()
    else:
        msg = "The toolchain (%s) you input is not supported" % args.toolchain
        print_string(msg, level="warning")
        return
    print_string("current toolchain is (%s) " % args.toolchain)
    if toolchain_class:
        if args.check_version:
            result = toolchain_class.check_version()
            if result:
                print_string("The toolchain verion is (%s) " % result)
            else:
                msg = "Please install (%s)" % args.toolchain
                print_string(msg, level="warning")
                return
        if args.install:
            print_string("Start to download ( %s with version %s)" % (args.toolchain, args.version))
            tgz_path = toolchain_class.download(version=args.version, path=args.download_path)
            if tgz_path:
                print_string("Start extracting files and installing toolchain")
                bin_path = toolchain_class.extract_file(tgz_path, path=args.extract_path)
                print_string("Start setting environmental variable")
                toolchain_class.set_env(path=bin_path)
                print_string("Please restart Terminal ")
                print_string("(%s) root is in (%s)" % (args.toolchain, bin_path))


def setup(subparser):
    subparser.add_argument(
        "--toolchain", default="gnu", help="Choose gnu")
    subparser.add_argument(
        "--check_version", action="store_true", help="Check toolchain version")
    subparser.add_argument(
        "--install", action="store_true", help="Download toolchain")
    subparser.add_argument(
        "--version", default="2017.09", help="Download the specified version toolchain")
    subparser.add_argument(
        "--download_path", help="Toolchain file will be download to this path")
    subparser.add_argument(
        "--extract_path", help="Toolchain file will be extracted to this path")
