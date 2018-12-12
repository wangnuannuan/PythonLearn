import unittest
from unittest import defaultTestLoader
import HTMLTestRunner
import coverage
import os
import tarfile
from embarc_tools.osp import repo, Git
from embarc_tools.download_manager import mkdir, cd, copy_file, untar, getcwd, delete_dir_files
from embarc_tools.utils import popen
pythonversion = os.environ.get("TRAVIS_PYTHON_VERSION") 
def deploy():
    file = "index.tar.gz"
    tar = tarfile.open(file, "w:gz")
    tar.add(pythonversion + "index.html")
    tar.close()
    repo_slug = os.environ.get("TRAVIS_REPO_SLUG")
    gh_token = os.environ.get("GH_TOKEN")
    url = "https://" + gh_token + "@github.com/" + repo_slug + ".git"
    mkdir("gh-pages")
    with cd("gh-pages"):
        git = Git()
        git.init(".")
        popen(["git", "remote", "add", "origin", url])
        git.fetch()
        popen(["git", "checkout", "-b", "gh-pages", "origin/gh-pages"])
        copy_file("../index.tar.gz", ".")
        untar(file, ".")
        delete_dir_files(file)
        git.add("--all")
        git.commit("deploy html")
        git.publish()
        # popen(["git", "push", url, "gh-pages:gh-pages"])


def get_allcase(case_path):
    discover = unittest.defaultTestLoader.discover(case_path, pattern="test*.py")
    return discover

if __name__ == '__main__':
    COV = coverage.coverage(branch=True, include='./embarc_tools/*')
    COV.start()
    testfilepath = pythonversion + "index.html"
    ftp = open(testfilepath,'wb')
    # runner = unittest.TextTestRunner()
    runner = HTMLTestRunner.HTMLTestRunner(stream=ftp, verbosity=2, title="test result")
    runner.run(get_allcase("."))
    ftp.close()
    deploy()
    COV.stop()
    COV.save()
    print('Coverage Summary:')
    COV.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, 'coverage')
    COV.html_report(directory=covdir)
    print('HTML version: file://%s/index.html' % covdir)
    print("See test result from https://wangnuannuan.github.io/PythonLearn")
    COV.erase()

