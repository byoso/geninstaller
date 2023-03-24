
"""The helpers are mainly functions shared with the other parts of
geninstaller"""


import os
import stat
import shutil
from distutils.dir_util import copy_tree

from silly_db.db import DB
from flamewok import color as c

from geninstaller.exceptions import GeninstallerError

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

GI_DIR = os.path.expanduser(
    "~/.local/share/applications-files/.geninstaller/")
APP_FILES_DIR = os.path.expanduser(
    "~/.local/share/applications-files/")
APP_DIR = os.path.expanduser(
    "~/.local/share/applications/")
DB_FILE = os.path.expanduser(
    "~/.local/share/applications-files/.geninstaller/gi_db.sqlite3")



def abort(content):
    message = f"{c.warning}Aborted: {content}{c.end}"
    print(message)
    exit()


def no_forbidden(el):
    if ";" in el:
        abort(f"forbidden use of ';' in: '{el}'")


def autoinstall():
    """install the empty database"""
    if not os.path.exists(DB_FILE):
        copy_tree(
            BASE_DIR+'/plop/database', GI_DIR)
        db = DB(
            base=GI_DIR,
            file=DB_FILE,
            migrations_dir="migrations")
        db.migrate_all()
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
            migrations_dir="migrations"
        )
    return gi_db


def display_list(apps):
    """apps are a silly-db Selection"""
    print("="*80)
    print(f"{'Geninstaller: Installed Applications':^80}")
    print("="*79 + "|")
    if len(apps) == 0:
        print("\nNo geninstaller application found")
        return
    for app in apps:
        print(
            f"NAME: '{app.name}'\n"
            f"COMMENTS: {app.comment}\n"
            f"TERMINAL ?: {app.terminal}\n"
            f"CATEGORIES: {app.categories}"
            )
        print("_"*79 + "|")


def clean_dir_name(name):
    """Cleans up the name for the directory"""
    cleaner = name.strip()
    cleaned_name = ""
    for letter in cleaner:
        if letter in list(" ;,/\\"):
            cleaned_name += "_"
        else:
            cleaned_name += letter
    return cleaned_name


def valid_for_installation(data):
    """Check the datas before copying anything

data = {
    "name": NAME,
    "exec": EXECUTABLE,
    "comment": DESCRIPTION,
    "terminal": TERMINAL,
    "icon": ICON,
    "categories": CATEGORIES,
    "base_dir": BASE_DIR,
    "exec_options": exec_options,
    "options": options,
}

    """
    for el in data.values():
        if type(el) == str:
            no_forbidden(el)
    gi_db = get_db()
    App = gi_db.model("application")
    app = App.sil.filter(f"name='{data['name']}'")
    if ("_" in data['name'] or "/" in data['name']
            or data['name'].startswith(".")):
        abort(
            "An app name must NOT contain '_' and '/', "
            "and must not begin with a '.'")

    if type(data['terminal']) != bool:
        abort("The 'TERMINAL' value must be a boolean")

    for category in data['categories']:
        no_forbidden(category)
    if len(app) > 0:
        abort(
            f"An application called '{data['name']}'"
            " is already installed, change the current application's"
            f" name, or uninstall the other application first."
            )
    # check relative paths
    base_dir = data['base_dir']
    exec = os.path.join(base_dir, data['exec'])
    icon = os.path.join(base_dir, data['icon'])
    if not os.path.exists(exec):
        abort("Wrong path to exec")
    if data['icon'] != '' and not os.path.exists(icon):
        abort("Wrong path to icon")


def create_desktop(datas):
    """Create the .desktop file and copy it to ~/.local/share/applications"""
    # compatibilité with old installer version < 1.1.3:
    try:
        datas['exec_options']
    except KeyError:
        datas['exec_options'] = ""
    try:
        datas['options']
    except KeyError:
        datas['options'] = []

    file_name = datas['applications']
    destination_dir = datas['applications_files']
    name = datas['name']
    exec = os.path.join(destination_dir, datas['exec'])
    if datas['exec_options'] != "":
        exec += " " + datas['exec_options']
    icon = os.path.join(destination_dir, datas['icon'])
    comment = datas['comment']
    terminal = datas['terminal']
    categories = datas['categories']
    content = (
        "[Desktop Entry]\n"
        f"Name={name}\n"
        f"Icon={icon}\n"
        f"Comment={comment}\n"
        f"Exec={exec}\n"
        f"Terminal={terminal}\n"
        f"Type=Application\n"
        )
    print(categories)
    if categories != "":
        content += f"Categories={categories}\n"
    for option in datas['options']:
        content += f"{option}\n"
    with open(file_name, "w") as file:
        file.write(content)
    set_executable(file_name)


def create_dir(datas):
    """Copy all the files in the root directory of the app to its
    right place, and ensure that the exec file is set 'executable'"""
    base_dir = datas['base_dir']
    destination_dir = datas['applications_files']
    try:
        shutil.copytree(
            base_dir, destination_dir)
    except FileExistsError:
        print(
            f"{c.warning}\nWarning: {destination_dir} "
            f"already exists before installation{c.end}"
            )

    exec = os.path.join(destination_dir, datas['exec'])
    set_executable(exec)
