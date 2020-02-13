import os,sys,inspect
current_lib_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0,current_lib_dir)

from lib.utils.commandline import *