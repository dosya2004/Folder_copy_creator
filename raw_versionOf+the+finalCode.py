import sys
import os
import shutil

logging = 'true'

def log(string):
    if logging == 'true':
        print(string)

def copy(path_src, path_des):
    try:
        log("FROM" + path_src + " TO:" + path_des)
        shutil.copy(path_src, path_des)
    except:
        log("File exists")

def each_file(path_src, path_des):

    for foldername, subfolders, filenames in os.walk(path_src):
        log('The curren folder is ' + foldername)

        for subfolder in subfolders:
            log('SUBFOLDER NAME ' + foldername + ': ' + subfolder)
            try:
                new_path = foldername.replace(path_src, path_des)
                os.mkdir(new_path+"\\"+subfolder)
            except:
                log("folder exists:" + subfolder)
        for filename in filenames:

            new_path = foldername.replace(path_src, path_des)
            file = foldername + '\\' + filename
            copy(file, new_path)


if sys.argv[i] == "-d":
    each_file(os.getcvd(), sys.argv[2])
if sys.argv[i] == "-s":
    each_file(sys.argv[2], os.getcwd())
