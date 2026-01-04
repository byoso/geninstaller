
"""The helpers are mainly functions shared with the other parts of
geninstaller"""


import os
import stat
import shutil
import subprocess
import venv
from pathlib import Path

from geninstaller.exceptions import GeninstallerError
from geninstaller.database import AppModel
from geninstaller.silly_engine import c

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

GI_DIR = os.path.expanduser(
    "~/.local/share/geninstaller-applications/.geninstaller/")
APP_FILES_DIR = os.path.expanduser(
    "~/.local/share/geninstaller-applications/")
APP_DIR = os.path.expanduser(
    "~/.local/share/applications/")


def copy_tree(src, dst) -> None:
    os.makedirs(dst, exist_ok=True)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copy_tree(s, d)
        else:
            shutil.copy2(s, d)


def abort(content)  -> None:
    message = f"{c.warning}Aborted: {content}{c.end}"
    print(message)
    exit()


def no_forbidden(el) -> None:
    if ";" in el:
        abort(f"forbidden use of ';' in: '{el}'")


def set_executable(file) -> None:
    """set a file executable"""
    st = os.stat(file)
    os.chmod(file, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def display_list(apps: list) -> None:
    """apps are a silly-db Selection"""
    print("="*80)
    print(f"{'Geninstaller: Installed Applications':^80}")
    print("="*79 + "|")
    if len(apps) == 0:
        print("\nNo geninstaller application found")
        return
    for app in apps:
        app = AppModel(**app)
        print(
            f"NAME: '{app.name}'\n"
            f"DESCRIPTION: {app.description}\n"
            f"TERMINAL ?: {app.terminal}\n"
            f"CATEGORIES: {app.categories}"
            )
        print("_"*79 + "|")


def clean_dir_name(name: str) -> str:
    """Cleans up the name for the directory"""
    cleaner = name.strip()
    cleaned_name = ""
    for letter in cleaner:
        if letter in list(" ;,/\\"):
            cleaned_name += "_"
        else:
            cleaned_name += letter
    return cleaned_name



def create_desktop(data: dict) -> None:
    """Create the .desktop file and copy it to ~/.local/share/applications"""

    try:
        data['exec_options']
    except KeyError:
        data['exec_options'] = ""
    try:
        data['options']
    except KeyError:
        data['options'] = []

    file_name = data['desktop_file']
    destination_dir = data['applications_files']
    name = data['name']

    # python program with dependencies in venv
    if data['python_dependencies'] != "":
        venv_path = os.path.join(destination_dir, ".venv", "bin", "python")
        executable = f'"{venv_path}" "{os.path.join(destination_dir, data["exec"])}"'
    else:
        executable = os.path.join(destination_dir, data['exec'])

    if data['exec_options'] != "":
        executable += " " + data['exec_options']
    icon = os.path.join(destination_dir, data['icon'])
    comment = data['description']
    terminal = "true" if data['terminal'] else "false"
    categories = data['categories']
    content = (
        "[Desktop Entry]\n"
        f"Name={name}\n"
        f"Icon={icon}\n"
        f"Comment={comment}\n"
        f"Exec={executable}\n"
        f"Terminal={terminal}\n"
        f"Type=Application\n"
        )

    if categories != "":
        content += f"Categories={categories}\n"
    for option in data['options']:
        content += f"{option}\n"
    with open(file_name, "w") as file:
        file.write(content)
    set_executable(file_name)


def create_dir(data: dict) -> None:
    """Copy all the files in the root directory of the app to its
    right place, and ensure that the exec file is set 'executable'"""
    base_dir = data['base_dir']
    destination_dir = data['applications_files']
    try:
        shutil.copytree(
            base_dir, destination_dir)
    except FileExistsError:
        print(
            f"{c.warning}\nWarning: {destination_dir} "
            f"already exists before installation{c.end}"
            )

    exec = os.path.join(destination_dir, data['exec'])
    set_executable(exec)


def create_venv(data: dict) -> None:
    """Create the virtual environment and install the python dependencies"""
    dependencies = data.get('python_dependencies', '')
    app_name = clean_dir_name(data['name'])
    venv_dir = Path(APP_FILES_DIR, app_name, ".venv")

    # Create the environment
    builder = venv.EnvBuilder(
        system_site_packages=True,  # otherwise, packages like GTK won't be accessible
        clear=True,
        with_pip=True,
    )
    builder.create(venv_dir)

    pip_path = venv_dir / "bin" / "pip"

    # upgrade pip
    subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
    # Install dependencies
    for dependency in dependencies.split(";"):
        dependency = dependency.strip()
        if not dependency:
            continue

        req_file = Path(APP_FILES_DIR) / app_name / dependency
        print("Installing:", req_file)

        subprocess.run([str(pip_path), "install", "-r", str(req_file)], check=True)


    print(f"Virtual environment created: {venv_dir.resolve()}")