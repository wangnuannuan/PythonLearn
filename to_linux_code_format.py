import os
import chardet
sum_log = "failed_build.log"
result_log = list()

def checkfolder(path):
    failed = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == "handler.log":
                failed = failed + 1
                file_encoding = chardet.detect(open(os.path.join(root, file), 'rb').read())['encoding']

                # if not ".git" in os.path.join(root, file) and (os.path.splitext(file)[-1] == ".ld"): 
                try:
                    with open(os.path.join(root, file), encoding=file_encoding) as f:
                        lines = f.readlines()
                        file_name = os.path.join(root, file)
                        result_log.append(file_name)
                        result_log.extend(lines)
                except Exception as e:
                    pass
                # print(os.path.join(root, file))
    result_log.append("Failed: " + str(failed))
    f = open(sum_log, "a")
    f.writelines(result_log)
    f.close()

def to_linux_code_format(path):
    failed = 0
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".c"):

                try:
                	os.system("indent -kr -i8 -ts8 -sob -ss -bs -psl "+ os.path.join(root, file))
                except Exception as e:
                    pass

if __name__ == "__main__":
    folder = "."
    to_linux_code_format(folder)
