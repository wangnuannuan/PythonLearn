from __future__ import print_function, division
from embarc_tools.project import *
from embarc_tools.utils import uniqify, popen
import unittest
import os
from embarc_tools.download_manager import cd


class TestIde(unittest.TestCase):
    def setUp(self):
        ospclass = osp.OSP()
        self.osp_root = ospclass.get_path("new_osp")
        self.app_path = os.path.join(self.osp_root, "example/baremetal/blinky")

    def test_generate(self):
        popen(["python","embarc_cli/embarc_tools/main.py", "build", "--path", self.app_path, "-g"])
        self.assertTrue(os.path.exists(os.path.join(self.app_path, file1)))
        self.assertTrue(os.path.exists(os.path.join(self.app_path,file2)))

    def tearDown(self):
        file1 = ".project"
        file2 = ".cproject"
        if os.path.exists(os.path.join(self.app_path, file1)):
            os.remove(os.path.join(self.app_path, file1))
        if os.path.exists(os.path.join(self.app_path, file2)):
            os.remove(os.path.join(self.app_path, file2))
        pass
