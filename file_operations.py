import os
import re
import chardet
import codecs
import io
import subprocess
import argparse
import difflib

def generate_diff(file1, file2):
    f1 = open(file1, 'r').readlines()
    f2 = open(file2, 'r').readlines()
    diffHTML = difflib.HtmlDiff()
    htmldiffs = diffHTML.make_file(f1, f2)
    with open('Comparison.html', 'w') as outFile:
        outFile.write(htmldiffs)


def check_source_file(fname, file_code):
    # Generic nits related to various source files
    # change = False

    with open(fname, encoding=file_code) as f:
        contents = f.read()
        current_cont = contents
        while True:
            contents_new = "\n".join(current_cont.splitlines())
            if contents_new != current_cont:
                current_cont = contents_new
                print("Please change ending lines at end of '{}'".format(fname))
            else:
                break

    if not current_cont.endswith("\n"):
        current_cont = current_cont + "\n"
        print("Missing newline at end of '{}'. Check your text "
                            "editor settings.".format(fname))

    if current_cont.startswith("\n"):
        print("Please remove blank lines at start of '{}'"
                            .format(fname))

    if current_cont.endswith("\n\n"):
        while True:
            current_cont = current_cont[:-1]
            print("Please remove blank lines at end of '{}'"
                                .format(fname))
            if current_cont.endswith("\n\n"):
                continue
            else:
                break

    return current_cont, contents


def crlf_2_lf(path):
    for root, _, files in os.walk(path, topdown=False):
        for f in files:
            result = subprocess.run(['file', '-bi', os.path.join(root, f)], stdout=subprocess.PIPE)
            file_code = result.stdout.decode().split("=")[-1]
            if file_code == "us-ascii":
                file_code = "ascii"
            code, _ = check_source_file(os.path.join(root, f), file_code)
            if code:
                with open(os.path.join(root, f), 'wb') as f:
                    f.write(code.encode(file_code))


def deal_lines(file_name):
    #cmd = "dos2unix -ascii %s" %file_name
    #os.system(cmd)
    with open(file_name, 'r') as f:
        for line in f:
            str = line.replace('\t', '    ').rstrip()
            yield str + "\n"


def tab_2_spaces(path):
    postfixes = ['.py', '.java', '.c', '.cpp', '.h']
    lineList = []
    for path, _, files in os.walk(path):
        for name in files:
            full_path = os.path.join(path, name)
            norm_path = os.path.normpath(os.path.abspath(full_path))
            modifyFileFlag = any([norm_path.endswith(postfix) for postfix in postfixes])
            if modifyFileFlag:
                for line in deal_lines(norm_path):
                    lineList.append(line)
                with open(norm_path, 'w+') as f:
                    for index in range(0, len(lineList)):
                        f.write(lineList[index])
                del lineList[:]


def to_linux_code_format(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".c"):
                try:
                	os.system("indent -kr -i8 -ts8 -sob -ss -bs -psl "+ os.path.join(root, file))
                except Exception as e:
                    print(e)
                    pass


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--crlf-2-lf", help="Replace crlf with lf in files under specify path")
    parser.add_argument("--diff", help="Compare two files and generate differences, please use comma to separate the two files")
    parser.add_argument("--tab-2-space", help="Replace tab with 4 spaces in files under specify path")
    parser.add_argument("--to-linux", help="Reformats a C language files under specify path")
    return parser.parse_args()


def main():
    options = parse_arguments()
    if options.crlf_2_lf:
        crlf_2_lf(options.crlf_2_lf)
    if options.diff:
        if not "," in options.diff:
            print("Parameter --diff in wrong format, please use comma to separate the two files")
        file1, file2 = options.diff.split(",")
        generate_diff(file1, file2)
    if options.tab_2_space:
        tab_2_spaces(options.tab_2_space)
    if options.to_linux:
        to_linux_code_format(options.to_linux)


if __name__ == "__main__":
    main()
