from __future__ import print_function, absolute_import, unicode_literals
import sys
import os
import subprocess
import time
from embarc_tools.settings import *
from .. download_manager import mkdir, delete_dir_files, cd
from embarc_tools.notify import (print_string, print_table)
from ..osp import osp
import collections
from embarc_tools.utils import pqueryOutputinline, pqueryTemporaryFile

BUILD_OPTION_NAMES=['BOARD', 'BD_VER', 'CUR_CORE', 'TOOLCHAIN', 'OLEVEL', 'V', 'DEBUG', 'SILENT', 'JTAG']
BUILD_INFO_NAMES=['EMBARC_ROOT', 'OUT_DIR_ROOT', 'BUILD_OPTION', 'APPLICATION_NAME', 'APPLICATION_LINKSCRIPT', 'APPLICATION_ELF', 'APPLICATION_BIN', 'APPLICATION_HEX', 'APPLICATION_MAP', 'APPLICATION_DUMP', 'APPLICATION_DASM', 'MIDDLEWARE', 'PERIPHERAL']
BUILD_CFG_NAMES=['EMBARC_ROOT', 'OUT_DIR_ROOT', 'COMPILE_OPT', 'CXX_COMPILE_OPT', 'ASM_OPT', 'AR_OPT', 'LINK_OPT', 'DEBUGGER', 'DBG_HW_FLAGS', 'MDB_NSIM_OPT']
BUILD_SIZE_SECTION_NAMES=['text', 'data', 'bss']

class embARC_Builder:
    def __init__(self, osproot=None, buildopts=None, outdir=None):
        self.buildopts = dict()
        make_options = ' '
        if osproot is not None and os.path.isdir(osproot):
            self.osproot = os.path.realpath(osproot)
            self.buildopts["EMBARC_ROOT"] = self.osproot
            make_options += 'EMBARC_ROOT=' + str(self.osproot) + ' '
        else:
            self.osproot = None
        if outdir is not None:
            self.outdir = os.path.realpath(outdir)
            make_options += 'OUT_DIR_ROOT=' + str(self.outdir) + ' '
        else:
            self.outdir = None

        if buildopts is not None:
            for opt in BUILD_OPTION_NAMES:
                if opt in buildopts:
                    self.buildopts[opt] = str(buildopts[opt]).strip()
                    option = str(opt) + '=' + self.buildopts[opt] + ' '
                    make_options += option
        self.make_options = make_options

        pass

    @staticmethod
    def build_common_check(app):
        build_status = {'result': True, 'reason':''}
        app_normpath = os.path.normpath(app)
        if os.path.isdir(app_normpath) == False:
            build_status['reason'] = 'Application folder doesn\'t exist!'
            build_status['result'] = False
        if not (os.path.exists(app_normpath+'/makefile') or \
                os.path.exists(app_normpath+'/Makefile') or \
                os.path.exists(app_normpath+'/GNUmakefile')):
            build_status['reason'] = 'Application makefile donesn\'t exist!'
            build_status['result'] = False

        app_realpath=os.path.realpath(app_normpath)
        build_status['app_path'] = app_realpath

        return app_realpath, build_status

    def configCoverity(self, toolchain):
        print_string("Config coverity")
        build_status = {'result': True, 'reason':''}
        self.coverity_comptype = 'gcc'
        self.coverity_compiler = 'arc-elf32-gcc'
        if toolchain == "gnu":
            pass
        elif toolchain == "mw":
            self.coverity_comptype = 'clangcc'
            self.coverity_compiler = 'ccac'
        else:
            build_status["result"] = False
            build_status["reason"] = "Toolchian is not supported!"
            return build_status
        self.coverity_sa_version = os.environ.get("COVERITY_SA_VERSION", None)
        self.coverity_server = os.environ.get("COVERITY_SERVER", None)
        self.user = os.environ.get("AUTO_USER", None)
        self.password = os.environ.get("AUTO_PASSWORD", None)
        self.coverity_steam_pre = os.environ.get("COVERITY_STREAM_PRE", None)
        return build_status

    def _setCoverityDirs(self, app):
        app_path_list = app.split("/")
        self.coverity_steam = self.coverity_steam_pre + "_".join(app_path_list[1:])
        # print_string("The coverity stream: {} {} {} ".format(self.coverity_steam))
        self.coverity_data_dir = os.environ.get("COVERITY_DATA_DIR", "coverity-data")
        self.coverity_config = os.path.join(self.coverity_data_dir, "coverity-config.xml")
        self.coverity_html = "coverity_html"
        if os.path.exists(self.coverity_data_dir):
            delete_dir_files(self.coverity_data_dir, dir=True)
            mkdir(self.coverity_data_dir)
        if os.path.exists(self.coverity_html):
            delete_dir_files(self.coverity_html, dir=True)

    def build_coverity(self, make_cmd):
        build_status = {'result': True, 'reason':''}
        print_string("BEGIN SECTION Configure Coverity to use the built-incompiler")
        config_compilercmd = "cov-configure --config {} --template --comptype {} --compiler {}".format(self.coverity_config,
            self.coverity_comptype, self.coverity_compiler)
        returncode = os.system(config_compilercmd)
        if returncode != 0 :
            build_status["result"] = False
            build_status["reason"] = "Configure Coverity Failed!"
            return build_status

        print_string("BEGIN SECTION Build with Coverity {}".format(self.coverity_sa_version))
        coverity_build = "cov-build --config %s --dir %s %s"%(self.coverity_config, self.coverity_data_dir, make_cmd)
        try: 
            build_proc = pqueryOutputinline(coverity_build, console=True)
            build_status['build_msg'] = build_proc
        except Exception as e:
            build_status["result"] = False
            build_status["reason"] = "Build with Coverity Failed!"
            return build_status

        print_string("BEGIN SECTION Coverity Analyze Defects")
        coverity_analyze = "cov-analyze --dir {}".format(self.coverity_data_dir)
        returncode = os.system(coverity_analyze)
        if returncode != 0 :
            build_status["result"] = False
            build_status["reason"] = "Coverity Analyze Defects Failed!"
            return build_status

        print_string("BEGIN SECTION Coverity Format Errors into HTML")
        coverity_errors = "cov-format-errors --dir %s -x -X --html-output %s"%(self.coverity_data_dir, self.coverity_html)
        returncode = os.system(coverity_errors)
        if returncode != 0 :
            build_status["result"] = False
            build_status["reason"] = "Coverity Format Errors into HTML Failed!"
            return build_status

        print_string("BEGIN SECTION Coverity Send E-mail Notifications")
        coverity_manage = "cov-manage-im --mode notification --execute --view 'Default' --host %s --user %s --password %s" %(self.coverity_server,
            self.user, self.password)
        returncode = os.system(coverity_manage)
        if returncode != 0 :
            build_status["result"] = False
            build_status["reason"] = " Coverity Send E-mail Notifications Failed!"
            return build_status

        print_string("BEGIN SECTION Coverity Commit defects to {} steam {}".format(self.coverity_server, self.coverity_steam))
        coverity_commit = "cov-commit-defects --dir %s --host %s --stream %s --user %s --password %s"%(self.coverity_data_dir,
            self.coverity_server, self.coverity_steam, self.user, self.password)
        returncode = os.system(coverity_commit)
        if returncode != 0 :
            build_status["result"] = False
            build_status["reason"] = "Coverity Commit defects Failed!"
            return build_status

        return build_status

    def build_target(self, app, target=None, parallel=8, coverity=False, silent=False):
        app_realpath, build_status = self.build_common_check(app)
        build_status['build_target'] = target
        build_status['time_cost'] = 0
        print_string("Build target: {} " .format(target))

        if build_status['result'] == False:
            return build_status

        ### Check and create output directory
        if self.outdir is not None and os.path.isdir(self.outdir) == False:
            print_string("Create application output directory: " + self.outdir)
            os.makedirs(self.outdir)

        build_precmd = "make "
        if parallel:
            build_precmd = "{} -j {}".format(build_precmd, str(parallel))
        build_precmd = "{} {}".format(build_precmd, self.make_options) #+= self.make_options
        if silent:
            if not "SILENT=1" in build_precmd:
                build_precmd = "{} SILENT=1 ".format(build_precmd)

        if type(target) is str or target is None:
            build_cmd = build_precmd + " " + str(target)
        else:
            build_status['reason'] = "Unrecognized build target"
            build_status['result'] = False
            return build_status

        if target != "info":
            build_config_template = self.get_build_template()
            with cd(app_realpath):
                self.get_makefile_config(build_config_template) # self.buildopts = 
            build_cmd_list = build_cmd.split()
            for i in range(len(build_cmd_list)):
                if build_cmd_list[i].startswith("EMBARC_ROOT"):
                    build_cmd_list[i] = "EMBARC_ROOT=" + self.osproot
            build_cmd = " ".join(build_cmd_list)
        print_string("Build command: {} ".format(build_cmd))
        build_status['build_cmd'] = build_cmd
        print_string("Start to build application")
        return_code = 0
        time_pre = time.time()
        if coverity:
            with cd(app_realpath):
                self._setCoverityDirs(app)
                coverity_build_status = self.build_coverity(build_cmd)
                if not coverity_build_status["result"]:
                    build_status["result"] = False
                    build_status["reason"] = coverity_build_status["reason"]
                    build_status["build_msg"] = coverity_build_status["build_msg"]
                else:
                    build_status["build_msg"] = ["Build Coverity successfully"]
        else:
            if target not in ["opt", "info", "size"]:
                with cd(app_realpath):
                    try:
                        return_code = os.system(build_cmd)
                        if return_code == 0:
                            build_status["build_msg"] = ["Build successfully"]
                        else:
                            build_status["build_msg"] = ["Build failed"]
                            build_status['result'] = False
                            build_status["reason"] = "ProcessError: Run command {} failed".format(build_cmd)
                    except (KeyboardInterrupt):
                        print_string("Terminate batch job", "warning")
                        sys.exit(1)
            else:
                try:
                    build_proc = pqueryOutputinline(build_cmd, cwd=app, console=True)
                    build_status['build_msg'] = build_proc
                except Exception as e:
                    print("Run command({}) failed!".format(build_cmd))
                    build_status["build_msg"] = ["Build failed"]
                    build_status["reason"] = "ProcessError: Run command {} failed".format(build_cmd)
                    build_status['result'] = False
        build_status['time_cost'] = (time.time() - time_pre)
        print_string("Completed in: ({})s  ".format(build_status['time_cost']))
        return build_status

    def get_build_info(self, app, parallel=False):
        build_status = self.build_target(app, target=str('opt'), parallel=parallel)
        if build_status['result'] == False:
            return build_status

        build_cfg = dict()
        cfg_lines = build_status['build_msg']

        for cfg_line in cfg_lines:
            words = cfg_line.split(':')
            if len(words) == 2:
                key = words[0].strip()
                value = words[1].strip()
                if key in BUILD_CFG_NAMES or key in BUILD_OPTION_NAMES:
                    build_cfg[key] = value

        build_status['build_cfg'] = build_cfg

        ### Get Build Info
        info_status = self.build_target(app, target=str('info'))
        build_out = info_status['build_msg']
        build_info = dict()
        if info_status['result']:
            # info_lines = build_out.splitlines()
            for info_line in build_out:#info_lines:
                words = info_line.split(':')
                if len(words) == 2:
                    key = words[0].strip()
                    value = words[1].strip()
                    if key in BUILD_INFO_NAMES:
                        build_info[key] = value
                    if key == 'BUILD_OPTION':
                       build_cfgs_dict = value.split()
                       for cfg_dict in build_cfgs_dict:
                           cfg_pair = cfg_dict.split('=')
                           if len(cfg_pair) == 2 and cfg_pair[0] in BUILD_OPTION_NAMES:
                               build_status['build_cfg'][cfg_pair[0]] = cfg_pair[1]
                    if key == 'MIDDLEWARE' or key == 'PERIPHERAL':
                        build_info[key+'S'] = value.split()
                    if key == 'APPLICATION_ELF':
                        build_info['APPLICATION_OUTDIR'] = os.path.dirname(value)
        build_status['build_info'] = build_info

        app_realpath = build_status['app_path']
        if 'EMBARC_ROOT' in build_status['build_cfg']:
            if not os.path.isabs((build_status['build_cfg']['EMBARC_ROOT'])):
                build_status['build_cfg']['EMBARC_ROOT'] = os.path.realpath(os.path.join(app_realpath, build_status['build_cfg']['EMBARC_ROOT']))
        if 'OUT_DIR_ROOT' in build_status['build_cfg']:
            if not os.path.isabs(build_status['build_cfg']['OUT_DIR_ROOT']):
                build_status['build_cfg']['OUT_DIR_ROOT'] = os.path.realpath(os.path.join(app_realpath, build_status['build_cfg']['OUT_DIR_ROOT']))
        if 'OUT_DIR_ROOT' in build_status['build_info']:
            if not os.path.isabs(build_status['build_info']['OUT_DIR_ROOT']):
                build_status['build_info']['OUT_DIR_ROOT'] = os.path.realpath(os.path.join(app_realpath, build_status['build_info']['OUT_DIR_ROOT']))
        if 'APPLICATION_ELF' in build_status['build_info']:
            if not os.path.isabs(build_status['build_info']['APPLICATION_ELF']):
                build_status['app_elf'] = os.path.realpath(os.path.join(app_realpath, build_status['build_info']['APPLICATION_ELF']))
            else:
                build_status['app_elf'] = build_status['build_info']['APPLICATION_ELF']
        if 'APPLICATION_HEX' in build_status['build_info']:
            if not os.path.isabs(build_status['build_info']['APPLICATION_HEX']):
                build_status['app_hex'] = os.path.realpath(os.path.join(app_realpath, build_status['build_info']['APPLICATION_HEX']))
            else:
                build_status['app_hex'] = build_status['build_info']['APPLICATION_HEX']
        if 'APPLICATION_BIN' in build_status['build_info']:
            if not os.path.isabs(build_status['build_info']['APPLICATION_BIN']):
                build_status['app_bin'] = os.path.realpath(os.path.join(app_realpath, build_status['build_info']['APPLICATION_BIN']))
            else:
                build_status['app_bin'] = build_status['build_info']['APPLICATION_BIN']
        if 'APPLICATION_OUTDIR' in build_status['build_info']:
            if not os.path.isabs(build_status['build_info']['APPLICATION_OUTDIR']):
                build_status['app_outdir'] = os.path.realpath(os.path.join(app_realpath, build_status['build_info']['APPLICATION_OUTDIR']))
            else:
                build_status['app_outdir'] = build_status['build_info']['APPLICATION_OUTDIR']

        return build_status

    def build_elf(self, app, parallel=False, pre_clean=False, post_clean=False, silent=False):
        ### Clean Application before build if requested
        if pre_clean:
            build_status = self.build_target(app, parallel=parallel, target=str('clean'))
            if build_status['result'] == False:
                return build_status

        ### Build Application
        build_status = self.build_target(app, parallel=parallel, target=str('all'), silent=silent)
        if build_status['result'] == False:
            return build_status
        ### Clean Application after build if requested
        if post_clean:
            clean_status = self.build_target(app, parallel=parallel, target=str('clean'))
            if clean_status['result'] == False:
                return clean_status

        return build_status

    def build_bin(self, app, parallel=False, pre_clean=False, post_clean=False):
        ### Clean Application before build if requested
        if pre_clean:
            build_status = self.build_target(app, parallel=parallel, target=str('clean'))
            if build_status['result'] == False:
                return build_status

        ### Build Application
        build_status = self.build_target(app, parallel=parallel, target=str('bin'))
        if build_status['result'] == False:
            return build_status
        ### Clean Application after build if requested
        if post_clean:
            clean_status = self.build_target(app, parallel=parallel, target=str('clean'))
            if clean_status['result'] == False:
                return clean_status

        return build_status

    def build_hex(self, app, parallel=False, pre_clean=False, post_clean=False):
        ### Clean Application before build if requested
        if pre_clean:
            build_status = self.build_target(app, parallel=parallel, target=str('clean'))
            if build_status['result'] == False:
                return build_status

        ### Build Application
        build_status = self.build_target(app, parallel=parallel, target=str('hex'))
        if build_status['result'] == False:
            return build_status
        ### Clean Application after build if requested
        if post_clean:
            clean_status = self.build_target(app, parallel=parallel, target=str('clean'))
            if clean_status['result'] == False:
                return clean_status

        return build_status

    def get_build_size(self, app, parallel=False, silent=False):
        build_status = self.build_target(app, parallel=parallel, target=str('size'), silent=silent)
        build_size = dict()
        if build_status['result'] == True:
            app_size_lines = build_status['build_msg']
            len_app_size_lines = len(app_size_lines)
            if len_app_size_lines >= 3:
                app_size_lines = app_size_lines[len_app_size_lines-2:]
                section_names = app_size_lines[0].split()
                section_values = app_size_lines[1].split()
                for idx, section_name in enumerate(section_names):
                    if section_name in BUILD_SIZE_SECTION_NAMES:
                        build_size[section_name] = int(section_values[idx])
            else:
                build_status['result'] = False
        else:
            print_string("Build failed and there is no size information")
        build_status['build_size'] = build_size
        return build_status

    def clean(self, app, parallel=False):
        build_status = self.build_target(app, target=str('clean'), parallel=parallel)
        return build_status

    def distclean(self, app, parallel=False):
        build_status = self.build_target(app, target=str('distclean'), parallel=parallel)
        return build_status

    def boardclean(self, app, parallel=False):
        build_status = self.build_target(app, target=str('boardclean'), parallel=parallel)
        return build_status

    def get_makefile_config(self, build_template=None):
        current_build_templates = dict()
        ospclass = osp.OSP()
        makefile, current_build_templates = ospclass.get_makefile_config(current_build_templates)
        osp_root = current_build_templates.get("EMBARC_OSP_ROOT", None)
        if osp_root:
            osp_root = osp_root.replace("\\", "/")

        osp_root, update = ospclass.check_osp(osp_root)
        if update:
            new_osp_dict = {"EMBARC_OSP_ROOT": osp_root}
            ospclass.update_makefile(new_osp_dict, os.getcwd())

        make_tool = "make"
        if current_build_templates.get("TOOLCHAIN")== "mw":
            make_tool = "gmake"
        opt_command = [make_tool]
        opt_command.append(str("opt"))
        try:
            returncode, cmd_output = pqueryTemporaryFile(opt_command)
            if not returncode:
                if cmd_output:
                    for opt_line in cmd_output:
                        if opt_line.startswith("APPL"):
                            current_build_templates["APPL"] = (opt_line.split(":", 1)[1]).strip()

                        build_template["APPL"] = current_build_templates.get("APPL")
                        if opt_line.startswith("BOARD"):
                            current_build_templates["BOARD"] = (opt_line.split(":", 1)[1]).strip()
                        build_template["BOARD"] = current_build_templates.get("BOARD")
                        if opt_line.startswith("BD_VER"):
                            current_build_templates["BD_VER"] = (opt_line.split(":", 1)[1]).strip()
                        build_template["BD_VER"] = current_build_templates.get("BD_VER")
                        if opt_line.startswith("CUR_CORE"):
                            current_build_templates["CUR_CORE"] = (opt_line.split(":", 1)[1]).strip()
                        build_template["CUR_CORE"] = current_build_templates.get("CUR_CORE")
                        if opt_line.startswith("TOOLCHAIN"):
                            current_build_templates["TOOLCHAIN"] = (opt_line.split(":", 1)[1]).strip()
                        build_template["TOOLCHAIN"] = current_build_templates.get("TOOLCHAIN")
                        if opt_line.startswith("EMBARC_ROOT"):
                            relative_root = (opt_line.split(":", 1)[1]).strip()
                            current_build_templates["EMBARC_OSP_ROOT"] = os.path.normpath(os.path.join(os.getcwd(), relative_root))
                        build_template["EMBARC_OSP_ROOT"] = current_build_templates.get("EMBARC_OSP_ROOT")
        except Exception as e:
            print_string("Error: {}".format(e))
            sys.exit(1)

        for option in self.make_options.split(" "):
            if "=" in option:
                [key, value] = option.split("=")
                if key in build_template:
                    build_template[key] = value
        print_string("Current configuration ")

        table_head = list()
        table_content = list()
        for key, value in build_template.items():
            table_head.append(key)
            table_content.append(value)
        msg = [table_head, [table_content]]
        print_table(msg)
        self.osproot = osp_root
        return build_template

    def get_build_template(self):

        build_template = {
            "APPL": "",
            "BOARD": "",
            "BD_VER": "",
            "CUR_CORE": "",
            "TOOLCHAIN": "",

        }
        build_template = collections.OrderedDict()
        return build_template
