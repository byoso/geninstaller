
"""The helpers are mainly functions shared with the other parts of
geninstaller"""


import os
import stat
import shutil
from distutils.dir_util import copy_tree

from silly_db.db import DB

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

GI_DIR = os.path.expanduser(
    "~/.local/share/applications-files/.geninstaller/")
APP_FILES_DIR = os.path.expanduser(
    "~/.local/share/applications-files/")
APP_DIR = os.path.expanduser(
    "~/.local/share/applications/")
DB_FILE = os.path.expanduser(
    "~/.local/share/applications-files/.geninstaller/gi_db.sqlite3")


def autoinstall():
    """install the empty database"""
    if not os.path.exists(DB_FILE):
        copy_tree(
            BASE_DIR+'/plop/database', GI_DIR)
        print("geninstaller database initialized")


def set_executable(file) -> None:
    """set a file executable"""
    st = os.stat(file)
    os.chmod(file, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def no_db():
    """check if the database already exists or not"""
    if not os.path.exists(DB_FILE):
        print("geninstaller's database has not been initialized.")
        return True
    else:
        return False


def get_db():
    if no_db:
        autoinstall()
    gi_db = DB(
            file=DB_FILE,
            base=GI_DIR,
        )
    return gi_db


def display_list(apps):
    """apps are a silly-db Selection"""
    if len(apps) == 0:
        print("No geninstaller application found")
        return
    print("="*119)
    print(f"{'Application':<45}|{'terminal ? ':^12}|{'Categories':<60}|")
    print("="*119 + "|")
    for app in apps:
        print(
            f"{app.name:<119}|\n"
            f"{app.comment:<45}|"
            f"{app.terminal:^12}|{app.categories:<60}|")
        print("_"*119 + "|")


def clean_name(name):
    cleaner = name.strip()
    dir_name = ""
    for letter in cleaner:
        if letter in list(" ;,/"):
            dir_name += "_"
        else:
            dir_name += letter
    return dir_name


def create_desktop(datas):
    """Create the .desktop file and copy it to ~/.local/share/applications"""
    file_name = datas['applications']
    destination_dir = datas['applications_files']
    name = datas['name']
    exec = os.path.join(destination_dir, datas['exec'])
    icon = os.path.join(destination_dir, datas['icon'])
    comment = datas['comment']
    terminal = datas['terminal']
    categories = datas['categories']
    desktop_categories = categories.replace("/", ";")
    content = (
        "[Desktop Entry]\n"
        f"Name={name}\n"
        f"Icon={icon}\n"
        f"Comment={comment}\n"
        f"Exec={exec}\n"
        f"Terminal={terminal}\n"
        f"Type=Application\n"
        f"Categories={desktop_categories}\n"
        )
    with open(file_name, "w") as file:
        file.write(content)
    set_executable(file_name)


def create_dir(datas):
    """Copy all the files in the root directory of the app to its
    right place, and ensure that the exec file is set 'executable'"""
    base_dir = datas['base_dir']
    destination_dir = datas['applications_files']
    shutil.copytree(
        base_dir, destination_dir)
    exec = os.path.join(destination_dir, datas['exec'])
    set_executable(exec)
