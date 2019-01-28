from __future__ import print_function, division, absolute_import, unicode_literals
import os
from embarc_tools.notify import print_string
from embarc_tools.settings import EMBARC_OSP_URL, get_input, SUPPORT_TOOLCHAIN
from ...osp import repo, osp
from ...download_manager import getcwd, download_file
from ...toolchain import gnu, metaware
help = "Set global build configuration."
usage = ("\n    embarc config build_cfg BOARD <value>\n"
        "    embarc config build_cfg BD_VER <value>\n"
        "    embarc config build_cfg CUR_CORE <value>\n")

def run(args, remainder=None):
    if len(remainder) != 2:
        print("usage: " + usage)
    else:
        config = remainder[0]
        if not config in ["BOARD", "BD_VER", "CUR_CORE"]:
            print("usage: " + usage)
            return
        value = remainder[1]
        osppath = osp.OSP()
        print_string("Set %s = %s as global setting" % (config, value))
        osppath.set_global(config, value)

def setup(subparser):
    subparser.usage = usage
