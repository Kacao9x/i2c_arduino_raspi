import subprocess
import re, os, glob
import unittest
from pathlib import *

#==============================================================================#
#Subprocess's call command with piped output and active shell
def Call(cmd):
    return subprocess.call(cmd, stdout=subprocess.PIPE,
                           shell=True)

#Subprocess's Popen command with piped output and active shell
def Popen(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            shell=True).communicate()[0].rstrip()

#Subprocess's Popen command for use in an iterator
def PopenIter(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            shell=True).stdout.readline

# display the file with keyword in ascending using BASH
def display_list_of_file(path, key):
    file_name = []
    list_cmd = ('ls '+ str(path) +' -1v' + " | grep '" + key + "'")
    print (list_cmd)
    for line in iter(PopenIter(list_cmd), ''):
        file_name.append(line.rstrip())

    print ('len filelist {}'.format(len(file_name)))
    return file_name


# display the file with keyword in ascending using BASH
def display_list_of_file_by_date(path, key):
    file_name = []
    list_cmd = "ls {} -1tr | grep '{}'".format(path, key)
    print (list_cmd)
    for line in iter(PopenIter(list_cmd), ''):
        file_name.append(line.rstrip())

    print ('len filelist {}'.format(len(file_name)))
    return file_name



def sort_folder_by_name_universal(path, key):
    def tryint(s):
        try:
            return int(s)
        except:
            return s

    def alphanum_key(s):
        # int_sort_list = []
        # for c in re.split('([0-9]+)', s.name):
        #     int_sort_list.append(tryint(c))
        # return int_sort_list
        return [ tryint(c) for c in re.split('([0-9]+)', s.name) ]

    # print ('path: {}'.format(path))
    # dirFiles = (os.listdir(os.path.join(path, key)))  # list of directory files

    print (path)
    dirFiles = [i for i in path.glob(key)]
    print (dirFiles)

    dirFiles.sort( key=alphanum_key )
    print ('\ndirFiles {}, len {}'.format(dirFiles, len(dirFiles)))

    return dirFiles




class Test(unittest.TestCase):
    def test_sort_universal(self):
        addr    = Path('/media/kacao/Ultra-Fit/titan-echo-boards/Nissan-Leaf/TC24-H77_190103/')
        sub_path= 'primary'
        key     = 'cycle2-*.dat'

        list_file_dat = sort_folder_by_name_universal(path=addr / sub_path, key=key)
        return

    def test_open_json(self):
        import json
        addr = Path('/media/kacao/Ultra-Fit/titan-echo-boards/Nissan-Leaf/TC04/')
        sub_path = 'primary_json'
        key = 'capture2_*.json'

        bucket = {
            'run': 2, 'walk': 4, 'swim': 10
        }



        list_file_dat = sort_folder_by_name_universal(path=(addr / sub_path).resolve(), key=key)
        print ('that {}'.format(list_file_dat))

        for i in list_file_dat:
        #     readout = Path(addr/sub_path/i).open('r')
        #     aCap = json.load(readout)
            print (i)
            with open(str(i)) as json_file:
                aCap = json.load(json_file)
            json_file.close()
            print (aCap)




        return