from __future__ import print_function, division, absolute_import, unicode_literals
try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import Request
    from urllib2 import urlopen
import re
import os
from distutils.spawn import find_executable
from embarc_tools.toolchain import ARCtoolchain, ProcessException
from embarc_tools.utils import pquery
from embarc_tools.notify import print_string
from .. download_manager import (download_file, extract_file, getcwd, mkdir, delete_dir_files)


class Gnu(ARCtoolchain):
    '''
    version: default version is 2017.09
    root_url: from this url to down load gnu
    pack: where the gnu archive is
    executable_name: a command will be used when check gnu
    '''
    root_url = "https://github.com/foss-for-synopsys-dwc-arc-processors/toolchain/releases"
    pack = None
    path = None
    executable_name = "arc-elf32-gcc"

    def __init__(self):

        exe = find_executable(self.executable_name)
        if exe:
            self.path = os.path.split(exe)[0]
            self.version = self.check_version()

    @staticmethod
    def check_version():
        '''run command "arc-elf32-gcc--version" and return current gnu version'''
        cmd = ["arc-elf32-gcc", "--version"]
        try:
            exe = pquery(cmd)
            if exe is None:
                msg = "can not execuate {}".format(cmd[0])
                print_string(msg, level="warning")
                return None
            version = re.search(r"[0-9]*\.[0-9]*", exe).group(0)
            if version:
                return version
        except ProcessException:
            return None

    def _set_version(self):
        '''get current gnu version and set the self.version'''
        version = self.check_version()
        if version:
            self.version = version

    def download(self, version=None, path=None):
        '''
        version - gnu version
        path - where the gnu package will be stored
        download gnu package and return the package path
        '''
        url = None
        pack_tgz = None
        if version:
            url = self.root_url + "/download/arc-" + version + "-release/arc_gnu_" + version + "_prebuilt_elf32_le_linux_install.tar.gz"
            pack_tgz = "arc_gnu_" + version + "_prebuilt_elf32_le_linux_install.tar.gz"
        else:
            url = "https://github.com" + self._lastest_url()
            version = re.search(r"[0-9]*\.[0-9]*", url).group(0)
            pack_tgz = url.rsplit("/", 1)[1]

        if path is None:
            path = getcwd()
        gnu_tgz_path = os.path.join(path, pack_tgz)
        if not os.path.exists(path):
            mkdir(path)
        if pack_tgz in os.listdir(path):
            print_string("GNU tgz already exists")
        else:
            print_string("Download from (%s)" % url)
            result = download_file(url, gnu_tgz_path)
            if not result:
                msg = "Download gnu failed"
                print_string(msg, level="error")
                gnu_tgz_path = None
        self.pack = gnu_tgz_path
        return gnu_tgz_path

    def extract_file(self, pack=None, path=None):
        '''extract gnu file from pack to path;
        pack - the path of the compressed package
        path - the compressed package is extracted to this path
        return the root path of gnu and set self.path'''
        if pack is None:
            pack = self.pack
        if path is None:
            path = getcwd()
        if pack is None:
            msg = "Please download gnu file first"
            print_string(msg, level="warning")
            return False

        else:
            file = pack.rsplit("/", 1)[1]
            version = re.search(r"[0-9]*\.[0-9]*", file).group(0)
            if version in os.listdir(path):
                delete_dir_files(version, True)
            try:
                gnu_file_path = extract_file(pack, path)
                return gnu_file_path
            except Exception as e:
                print(e)
            '''
            if gnu_file_path is not None:
                self.path = os.path.join(path, version, "bin")
                shutil.move(gnu_file_path, version)
                return self.path
            '''

    def set_env(self, path=None):
        '''set environment'''
        self.set_toolchain_env("gnu", path)

    def _lastest_url(self):
        pattern = re.compile('<ul.*?class="mt-1 mt-md-2">(.*?)</ul>', re.S | re.M)
        pattern2 = re.compile('<a.*?href=(.*?) rel="nofollow" class="d-flex flex-items-center".*?<svg.*?<strong.*?</a>', re.S | re.M)
        pack_format = "_ide_win_install.exe" if self.get_platform() == "Windows" else "_prebuilt_elf32_le_linux_install.tar.gz"
        try:
            request = Request(self.root_url)
            response = urlopen(request)
            content = response.read().decode('utf-8')

            items = re.findall(pattern, content)
            latesturl = None

            for item in items:
                itemsnow = re.findall(pattern2, item)
                for i in itemsnow:
                    if pack_format in i:
                        latesturl = i.strip('"')
                        break
                if latesturl:
                    break
            return latesturl
        except urllib2.URLError as e:
            if hasattr(e, "code"):
                print_string(e, level="warning")
            if hasattr(e, "reason"):
                print_string(e.reason, level="warning")
        else:
            print_string("Can not get latest veriosn Gnu")
