from __future__ import print_function, division, absolute_import, unicode_literals
import os
from embarc_tools.notify import print_string
from embarc_tools.settings import EMBARC_OSP_URL
from ..osp import repo, osp
from ..download_manager import getcwd
from ..toolchain import gnu, metaware
help = "Get, set or unset configuration options."

description = (
        "Options can be global (via the --global switch) or local (per program)\n"
        "Global options are always overridden by local/program options.\n"
        "Currently supported options: osp, toolchain")

def run(args, remainder=None):
    if args.var == "osp":
        variable = args.value
        if repo.Repo.isurl(variable):
            if variable.endswith("zip"):
                pass

            elif variable == EMBARC_OSP_URL:
                osprepo = repo.Repo.fromurl(variable)
                path = getcwd()
                if not os.path.exists(osprepo.name):
                    osprepo.clone(osprepo.url, path=os.path.join(path, osprepo.name), rev=None, depth=None, protocol=None, offline=False)
                    print_string("Finish clone {}".format(osprepo.name))
                    osp_path.set_path(os.path.join(path, osprepo.name), osprepo.url) ####
                    print_string("Add (%s) to user profile osp.yaml" % os.path.join(path, osprepo.name))
                else:
                    print_string("There is already a folder or file named 'embarc_osp' under current path")
                    return

            else:
                print_string("Please specific right url to get EMBARC_OSP using --var ")

        elif not os.path.exist(variable):
            pass
        else:
            print_string("Current global setting about osp")
            '''get from osp.json'''
        if args.list:
            '''list all setting about osp'''
            pass

    elif args.var == "toolchain":
        variable = args.value
        if variable:
            if variable == "gnu":
                pass
            elif variable == "mw":
                pass
            else:
                print_string("This toolchain {} is not supported now".format(variable))
        else:
            gnu_verion = gnu.Gnu.check_version()
            mw_verion = metaware.Mw.check_version()
            if gnu_verion:
                print_string("Current GNU verion: {}".format(gnu_verion))
            else:
                
            if mw_verion:
                print_string("Current MetaWare version:")

            





def setup(subparser):
    subparser.add_argument(
        "--var", nargs='?',  help='Variable name. E.g. "osp", "toolchain"')
    subparser.add_argument(
        "--value", nargs='?', help="Value. Will show the currently set default value for a variable if not specified.")
    subparser.add_argument(
        '-G', '--global', action='store_true', help="Set as global settings, not local")
    subparser.add_argument(
        '-U', '--unset', action='store_true', help="Unset the specified variable.")
    subparser.add_argument(
        '-L', '--list', action='store_true', help="List all configuration")
    subparser.add_argument(
        "--clone", action="store_true", help="clone embarc_osp")
