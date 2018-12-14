from __future__ import print_function, division, absolute_import, unicode_literals
from ..osp import repo, osp
import os
from ..download_manager import getcwd
from embarc_tools.notify import (print_string, print_table)

help = "Set embarc osp"

def run(args):
    if not any([args.list ,args.clone]):
        msg = "Please select a parameter [--clone, --list]"
        print_string(msg, level="warning")
    osp_path = osp.OSP()

    if args.list:
        print_string("The current recorded path of osp")
        osp_path.list_path()
    if args.clone:
        url = "https://github.com/foss-for-synopsys-dwc-arc-processors/embarc_osp"
        print_string("Clone embarc_osp from (%s)" % url)
        osprepo = repo.Repo.fromurl(url)
        path = getcwd()
        if not os.path.exists(osprepo.name):
            osprepo.clone(osprepo.url, path=os.path.join(path, osprepo.name), rev=None, depth=None, protocol=None, offline=False)
            print_string("Finish clone {}".format(osprepo.name))
            osp_path.set_path(os.path.join(path, osprepo.name), osprepo.url)
            print_string("Add (%s) to user profile osp.yaml" % os.path.join(path, osprepo.name))
        else:
            print_string("There is already a folder or file named 'embarc_osp' under current path")

def setup(subparser):
    subparser.add_argument(
        "--clone", action="store_true", help="clone embarc_osp")
    subparser.add_argument(
        "--list", action="store_true", help="List osp path")


