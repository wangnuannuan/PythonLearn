from __future__ import print_function, absolute_import, unicode_literals
import platform

OSP_DIRS = ["arc", "board", "device", "inc", "library", "middleware"]
OLEVEL = ["Os", "O0", "O1", "O2", "O3"]
GNU_PATH = ""
MW_PATH = ""
SUPPORT_TOOLCHAIN = ["gnu", "mw"]
OSP_PATH = ""
CURRENT_PLATFORM = platform.system()
PYTHON_VERSION = platform.python_version()
MAKEFILENAMES = ['Makefile', 'makefile', 'GNUMakefile']
MIDDLEWARE = [
    "aws",
    "coap",
    "common",
    "fatfs",
    "http_parser",
    "ihex",
    "lwip-contrib",
    "Lwip",
    "mbedtls",
    "mqtt",
    "ntshell",
    "openthread",
    "parson",
    "u8glib",
    "wakaama"
]

LIBRARIES = ["clib", "secureshield"]

BUILD_CONFIG_TEMPLATE = {
    "APPL": "",
    "BOARD": "",
    "BD_VER": "",
    "CUR_CORE": "",
    "TOOLCHAIN": "",
}


def get_input(input_str):
    if PYTHON_VERSION.startswith("2"):
        return raw_input(input_str)
    else:
        return input(input_str)
