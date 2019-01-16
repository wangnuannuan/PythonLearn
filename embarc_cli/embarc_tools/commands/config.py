from __future__ import print_function, division, absolute_import, unicode_literals
import os
from embarc_tools.notify import print_string
from embarc_tools.settings import EMBARC_OSP_URL, get_input
from ..osp import repo, osp
from ..download_manager import getcwd, download_file
from ..toolchain import gnu, metaware
help = "Get, set or unset configuration options."

description = (
        "Currently supported options: osp, toolchain")

def run(args, remainder=None):
    pass



def setup(subparser):
    subparser.usage = ("\n    embarc config osp [--add] <name> <url/path>\n"
        "    embarc config osp [--rename] <old> <new>\n"
        "    embarc config osp [--remove] <name>\n"
        "    embarc config toolchain [--version] [--download] gnu\n"
        "    embarc config toolchain [--version] mw\n")

