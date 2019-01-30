import unittest
from unittest import defaultTestLoader
import HTMLTestRunner
import coverage
import os
import tarfile
from embarc_tools.osp import repo, Git, osp
from embarc_tools.download_manager import mkdir, cd, copy_file, untar, getcwd, delete_dir_files
from embarc_tools.utils import popen
from embarc_tools.toolchain import gnu
from embarc_tools.settings import EMBARC_OSP_URL
from embarc_tools.notify import print_string
pythonversion = os.environ.get("TRAVIS_PYTHON_VERSION")


def deploy():
    file = "index.tar.gz"
    tar = tarfile.open(file, "w:gz")
    tar.add(pythonversion + "index.html")
    for root, _, files in os.walk("coverage"):
        for file in files:
            fullpath = os.path.join(root, file)
            tar.add(fullpath, arcname=file)
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
        print("start untar file index.tar.gz")
        untar(file, ".")
        print("delete index.tar.gz")
        popen(["ls"])
        delete_dir_files(file)
        git.add("--all")
        git.commit("deploy html")
        try:
            print("start to deploy")
            git.publish()
        except Exception as e:
            print("pull code")
            popen(["git", "pull", url, "gh-pages"])
            git.publish()
        # popen(["git", "push", url, "gh-pages:gh-pages"])


def get_allcase(case_path):
    discover = unittest.defaultTestLoader.discover(case_path, pattern="test*.py")
    return discover


def before_install():
    os.system("pycodestyle embarc_tools --ignore=E501")
    os.system("pyflakes embarc_tools")
    ospclass = osp.OSP()
    url = EMBARC_OSP_URL
    osprepo = repo.Repo.fromurl(url)
    path = getcwd()
    source_type = "git"
    name = "new_osp"
    if not os.path.exists(name):
        print_string("Start clone {}".format(osprepo.name))
        osprepo.clone(osprepo.url, path=os.path.join(path, name), rev=None, depth=None, protocol=None, offline=False)
        print_string("Finish clone {}".format(osprepo.name))
        ospclass.set_path(name, source_type, os.path.join(path, name), url)
        print_string("Add (%s) to user profile osp.json" % os.path.join(path, osprepo.name))
    if ospclass.get_path(str("new_osp")):
        config = "EMBARC_OSP_ROOT"
        ospclass.set_global(config, str("new_osp"))

if __name__ == '__main__':
    COV = coverage.coverage(branch=True, include='./embarc_tools/*')
    COV.start()
    before_install()
    testfilepath = pythonversion + "index.html"
    ftp = open(testfilepath, 'wb')
    # runner = unittest.TextTestRunner()
    runner = HTMLTestRunner.HTMLTestRunner(stream=ftp, verbosity=2, title=pythonversion)
    runner.run(get_allcase("."))
    ftp.close()
    COV.stop()
    COV.save()
    print('Coverage Summary:')
    COV.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, 'coverage')
    COV.html_report(directory=covdir)
    deploy()
    print('HTML version: file://%s/index.html' % covdir)
    print("See test result from https://wangnuannuan.github.io/PythonLearn")
    COV.erase()
