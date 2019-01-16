from __future__ import print_function, division, absolute_import, unicode_literals
import os
from embarc_tools.notify import print_string
from embarc_tools.settings import EMBARC_OSP_URL, get_input
from ...osp import repo, osp
from ...download_manager import getcwd, download_file
from ...toolchain import gnu, metaware
help = "Get, set or unset osp configuration."

usage = ("\n    embarc config osp --add [<--clone>] <name> <url/path>\n"
        "    embarc config osp --rename <old> <new>\n"
        "    embarc config osp --remove <name>")

def run(args, remainder=None):
    osppath = osp.OSP()
    num = [args.add, args.rename, args.remove]
    if num.count(False) + num.count(None) < 2:
        print("usage: " + usage)
        return
    if args.add:
        if len(remainder) != 2:
            print("usage: " + usage)
        else:
            name = remainder[0]
            url = remainder[1]
            if os.path.exists(url) and os.path.isdir(url):
                source_type = "local"
                osppath.set_path(name, source_type, url)

            elif repo.Repo.isurl(url):
                if url.endswith("zip"):
                    name = name + ".zip"
                    result = download_file(url, name)
                    if not result:
                        msg = "Download zip failed"
                        print_string(msg, level="error")
                    else:
                        source_type = "zip"
                        osppath.set_path(name, source_type, os.path.join(path, name), url)
                elif url == EMBARC_OSP_URL:
                    osprepo = repo.Repo.fromurl(url)
                    path = getcwd()
                    if not os.path.exists(name):
                        osprepo.clone(osprepo.url, path=os.path.join(path, name), rev=None, depth=None, protocol=None, offline=False)
                        print_string("Finish clone {}".format(osprepo.name))
                        source_type = "git"
                        osppath.set_path(name, source_type, os.path.join(path, name), url)
                        print_string("Add (%s) to user profile osp.json" % os.path.join(path, osprepo.name))
                    else:
                        print_string("There is already a folder or file named 'embarc_osp' under current path")
                        return
            else:
                print_string("Please specific right value using --var ")

    elif args.rename:
        if len(remainder) != 2:
            print("usage: " + usage)
        else:
            old = remainder[0]
            new = remainder[1]
            osppath.rename(old, new)
    elif args.remove:
        name = args.remove
        osppath.remove_path(name)
    else:
        print("usage: " + usage)




def setup(subparser):
    subparser.usage = usage
    subparser.add_argument(
        "--add", action='store_true',  help='Fetch the remote source code and add it to osp.json')
    subparser.add_argument(
        "--rename", action='store_true', help="Rename osp source code.")
    subparser.add_argument(
        '-rm', '--remove',  help="Remove the specified osp source code.")
