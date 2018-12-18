from __future__ import print_function, division
from embarc_tools.toolchain import gnu, metaware, ARCtoolchain
import unittest
import os, shutil

class TestToolchain(unittest.TestCase):
    def setUp(self):
        super(TestToolchain, self).setUp()
        self.gnu = gnu.Gnu()
        self.mw = metaware.Mw()
        self.pack = os.path.join(os.getcwd(),"arc_gnu_2018.09_prebuilt_elf32_le_linux_install.tar.gz")

    def test_is_support(self):
        result = ARCtoolchain.is_supported("gnu")
        self.assertTrue(result)
        result = ARCtoolchain.is_supported("mw")
        self.assertTrue(result)

    def test_get_platform(self):
        result = ARCtoolchain.get_platform()
        self.assertIn(result, ["Windows", "Linux"])

    def test_check_version(self):
        gnuversion = self.gnu.check_version()
        print(gnuversion)
        mwversion = self.mw.check_version()
        print(mwversion)

    def test_download(self):
        gnu_tgz_path = self.gnu.download(version="2018.09")
        print("download ",gnu_tgz_path)
        print(os.listdir("."))

        self.assertIsNotNone(gnu_tgz_path)

    def test_extract_file(self):
        pack = "arc_gnu_2018.09_prebuilt_elf32_le_linux_install.tar.gz"
        path = self.gnu.extract_file(self.pack)
        print("gnu pack path: ",path)

    def test_set_toolchain_env(self):
        pass
        # self.gnu.set_toolchain_env("")

    def tearDown(self):
        if os.path.exists(self.pack):

            os.remove(self.pack)
        if os.path.exists("2018.09"):
            shutil.rmtree("2018.09")


