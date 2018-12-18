from __future__ import print_function, division, absolute_import, unicode_literals
import os
import yaml
from embarc_tools.notify import (print_string, print_table, COLORS)
from embarc_tools.settings import MAKEFILENAMES, get_input, OSP_DIRS
from embarc_tools.exporter import Exporter
from ..download_manager import generate_yaml, edit_yaml, cd


class OSP(object):
    def __init__(self, osp_file="osp.yaml"):
        self.path = os.path.join(os.path.expanduser("~"), '.embarc_cli')
        if not os.path.exists(self.path):
            try:
                os.mkdir(self.path)
            except (IOError, OSError):
                pass
        self.file = osp_file

        fl = os.path.join(self.path, self.file)
        if not os.path.exists(fl):
            self.cfg_dict = None
            try:
                generate_yaml(fl, self.cfg_dict)
            except Exception as e:
                print("[embARC] Write file failed: {}".format(e))
        else:
            self.cfg_dict = yaml.load(fl)
        self.current = self.get_path()

    def set_path(self, path, url=None):
        fl = os.path.join(self.path, self.file)
        path = path.replace("\\", "/")
        try:
            with open(fl) as f:
                self.cfg_dict = yaml.load(f)
                if self.cfg_dict:
                    for _, path_dict in self.cfg_dict.items():
                        for _, path_ in path_dict.items():
                            if path == path_:
                                return
                path_num = 0
                if self.cfg_dict:
                    path_num = len(self.cfg_dict)
                else:
                    self.cfg_dict = dict()
                path_key = "path" + str(path_num + 1)
                self.cfg_dict[path_key] = dict()
                self.cfg_dict[path_key]["git"] = url
                self.cfg_dict[path_key]["local"] = path
                self.current = path
                edit_yaml(fl, self.cfg_dict)

        except IOError:
            raise IOError("Can not open file %s ." % fl)

    def get_path(self):
        fl = os.path.join(self.path, self.file)
        try:
            with open(fl) as f:
                self.cfg_dict = yaml.load(f)
                if self.cfg_dict:
                    for _, path_dict in self.cfg_dict.items():
                        if path_dict.get("local", None):
                            osp_root = path_dict["local"]
                            if self.is_osp(osp_root):
                                return osp_root
                return None

        except IOError:
            raise IOError("Can not open file %s ." % fl)

    def clear_path(self):
        fl = os.path.join(self.path, self.file)
        try:
            self.cfg_dict = dict()
            edit_yaml(fl, self.cfg_dict)

        except IOError:
            raise IOError("Can not open file %s ." % fl)

    def list_path(self):
        fl = os.path.join(self.path, self.file)

        try:
            with open(fl) as f:
                self.cfg_dict = yaml.load(f)

                table_head = ["osp"]
                table_content = list()
                if self.cfg_dict:
                    for path, path_dict in self.cfg_dict.items():
                        table_content.append([path])
                        string_list = list()
                        for (key, value) in path_dict.items():
                            if value == self.current:
                                value = COLORS['green'] + value + COLORS['default']
                            string_list.append(" %s: %s" % (key, value))
                        # string_list = [ " %s: %s" % (key, value) for (key, value) in path_dict.items()]
                        string = "\n".join(string_list)
                        table_content.append([string])
                    msg = [table_head, table_content]
                    print_table(msg)
                else:
                    print_string("There is no valid osp root path in record")

        except IOError:
            raise IOError("Can not open file %s ." % fl)

    def is_osp(self, path):
        if self.cfg_dict:
            for key, path_dict in self.cfg_dict.items():
                if path == key:
                    if "local" in path_dict:
                        path = path_dict["local"]
                        return path
        if os.path.exists(path) and os.path.isdir(path):
            for files in OSP_DIRS:
                files_path = os.path.join(path, files)
                if os.path.exists(files_path) and os.path.isdir(files_path):
                    pass
                else:
                    return False
            self.set_path(path=path, url=None)
            return path
        else:
            return False

    def support_board(self, root):
        result = []
        board_path = os.path.join(root, "board")
        if os.path.exists(board_path):
            for file in os.listdir(board_path):
                if os.path.isdir(os.path.join(board_path, file)):
                    result.append(file)
        return result

    def get_board_version(self, root, board, bd_version=None):
        result = []
        board_path = "board/" + board
        ver_path = os.path.join(root, board_path)
        if os.path.exists(ver_path):
            bd_vers_dict = self._board_version_config(root, board, bd_version)
            result.extend(bd_vers_dict.keys())
        return result

    def _board_version_config(self, root, board, bd_version=None):
        board_path = os.path.join(root, "board", board)
        bd_vers = dict()
        if os.path.exists(board_path):
            files = os.listdir(board_path)
            if "configs" in files:
                versions = os.listdir(os.path.join(board_path, "configs"))
                for version in versions:
                    version_path = os.path.join(board_path, "configs", version)
                    if os.path.isdir(version_path):
                        bd_vers[version] = version_path
            else:
                versions = os.listdir(board_path)
                for version in versions:
                    path = os.path.join(board_path, version)
                    if os.path.isdir(path) and "configs" in os.listdir(path):
                        version_path = os.path.join(board_path, version, "configs")
                        bd_vers[version] = version_path
        if bd_version is not None:
            if bd_version in bd_vers:
                bd_ver = {bd_version: bd_vers[bd_version]}
                return bd_ver
        return bd_vers

    def get_tcfs(self, root, board, bd_version, cur_core=None):
        result = []
        board_version_path_dict = self._board_version_config(root, board, bd_version)
        board_path = board_version_path_dict[bd_version]
        cur_core_file = cur_core + ".tcf" if cur_core else cur_core
        if os.path.exists(board_path):
            for root, _, files in os.walk(board_path, topdown=True):
                if cur_core_file in files:
                    result.append(cur_core)
                    break
                for file in files:
                    filename, filesuffix = os.path.splitext(file)
                    if filesuffix != ".tcf":
                        continue
                    else:
                        result.append(filename)

        return result

    def get_makefile(self, app_path):
        for makefile in MAKEFILENAMES:
            makefile_path = os.path.join(app_path, makefile)
            if os.path.exists(makefile_path) and os.path.isfile(makefile_path):
                return makefile_path
        return None

    def check_osp(self, path):
        update = False
        if path:
            osp_root = path.replace("\\", "/")
        else:
            osp_root = path
        if not osp_root or not self.is_osp(osp_root):
            update = True
            msg = "Current EMBARC_ROOT is not a valid osp root"
            level = "warning"
            print_string(msg, level)
            self.list_path()
            while True:
                input_root = get_input("Choose osp root or set another path as osp root: ")
                osp_root = self.is_osp(input_root)

                if not osp_root:
                    msg = "What you choose is not a valid osp root"
                    level = "warning"
                    print_string(msg, level)
                    osp_root = self.get_path()
                    if osp_root:
                        print_string("Here choose " + osp_root + " as osp root")
                        break
                    else:
                        self.clear_path()
                        print_string("Please set a valid osp root or download embarc osp first")
                        continue

                break
            osp_root = osp_root.replace("\\", "/")
            self.set_path(osp_root)
        return osp_root, update

    def get_makefile_config(self, build_template=None, verbose=False):
        '''
        Get config from makefile
        '''
        print_string("Read makefile and get configuration ")
        makefile = None
        for file in MAKEFILENAMES:
            if os.path.exists(file) and os.path.isfile(file):
                makefile = file

        if not makefile:
            print_string("Makefile doesn't exists")
            return makefile, build_template

        with open(makefile) as f:
            lines = f.read().splitlines()
            for line in lines:
                if line.startswith("APPL "):
                    build_template["APPL"] = (line.split("=")[1]).strip()

                if line.startswith("BOARD"):
                    build_template["BOARD"] = (line.split("=")[1]).strip()
                if line.startswith("BD_VER"):
                    build_template["BD_VER"] = (line.split("=")[1]).strip()
                if line.startswith("CUR_CORE"):
                    build_template["CUR_CORE"] = (line.split("=")[1]).strip()
                if line.startswith("TOOLCHAIN"):
                    build_template["TOOLCHAIN"] = (line.split("=")[1]).strip()
                    if build_template["TOOLCHAIN"] and build_template["TOOLCHAIN"] != "":
                        pass
                    else:
                        build_template["TOOLCHAIN"] = "gnu"
                if line.startswith("EMBARC_ROOT"):
                    relative_root = (line.split("=")[1]).strip()
                    osp_root = os.path.normpath(os.path.join(os.getcwd(), relative_root))
                    build_template["EMBARC_OSP_ROOT"] = osp_root
                if verbose:
                    if line.startswith("MID_SEL"):
                        build_template["middleware"] = (line.split("=")[1]).strip()
                    if line.startswith("APPL_CSRC_DIR"):
                        build_template["csrc"] = (line.split("=")[1]).strip()
                    if line.startswith("APPL_ASMSRC_DIR"):
                        build_template["asmsrc"] = (line.split("=")[1]).strip()
                    if line.startswith("APPL_INC_DIR"):
                        build_template["include"] = (line.split("=")[1]).strip()
                    if line.startswith("APPL_DEFINES"):
                        build_template["defines"] = (line.split("=")[1]).strip()
                    if line.startswith("OS_SEL"):
                        os_sel = (line.split("=")[1]).strip()
                        if os_sel and os_sel != "":
                            build_template["os"] = os_sel
                    if line.startswith("LIB_SEL"):
                        lib_sel = (line.split("=")[1]).strip()
                        if lib_sel and lib_sel != "":
                            build_template["lib"] = lib_sel

        return makefile, build_template

    def update_makefile(self, value, path):
        """ update embarc_root in makefile"""
        with cd(path):
            print_string("Update makefile {}".format(value))
            build_template = dict()
            makefile, build_template = self.get_makefile_config(build_template, verbose=True)
            build_template.update(value)
            exporter = Exporter("application")
            exporter.gen_file_jinja("makefile.tmpl", build_template, makefile, os.getcwd())
