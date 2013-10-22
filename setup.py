from cx_Freeze import setup, Executable
import shutil
import os, sys, inspect
cwd = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))


exe = Executable(script='pwt.py', base='Win32GUI', targetName='PWT.exe', compress=True,
    icon=os.path.join(cwd, 'icons', 'PWT.ico'))

setup(name='PWT', version='1.0', description='Python Windows Tiler',
    author='Tzbob, 7enderhead, mm318', executables=[exe])

root_dir = os.path.join(cwd, 'build')
src_dir = os.path.join(cwd, 'icons')

for file_dir in os.listdir(root_dir):
    file_dir_path = os.path.join(root_dir, file_dir)
    if(os.path.isdir(file_dir_path)):
    	dst_dir = os.path.join(file_dir_path, 'icons')
        shutil.copytree(src_dir, dst_dir)

