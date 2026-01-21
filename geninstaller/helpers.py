
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
        f"Path={destination_dir}\n"
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


def has_ensurepip(python_bin: str) -> bool:
    """Return True if the given Python binary has ensurepip available."""
    try:
        subprocess.run(
            [python_bin, "-m", "ensurepip", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def create_venv(data: dict) -> None:
    """Create the virtual environment and install the Python dependencies"""
    dependencies = data.get('python_dependencies', '')
    app_name = clean_dir_name(data['name'])
    venv_dir = Path(APP_FILES_DIR, app_name, ".venv")

    # Remove existing venv to ensure clean creation
    if venv_dir.exists():
        shutil.rmtree(venv_dir)

    python_bin = data.get('python_required_version', 'python3')
    if not python_bin:  # None or empty string
        python_bin = "python3"

    # Check if ensurepip is available
    can_use_ensurepip = has_ensurepip(python_bin)

    venv_command = [
        python_bin,
        "-m", "venv",
        "--clear",
        "--system-site-packages",
        str(venv_dir),
    ]

    # If ensurepip is missing, create venv without pip
    if not can_use_ensurepip:
        venv_command.insert(-1, "--without-pip")

    subprocess.run(venv_command, check=True)

    python_in_venv = venv_dir / "bin" / "python"
    pip_in_venv = venv_dir / "bin" / "pip"

    if not can_use_ensurepip:
        print(
            f"\n⚠️ {c.warning}Warning: using a non-system Python ({python_bin}). {c.end}\n"
            f"{c.warning}System packages (like gi/GTK) may not be available !{c.end}\n"
            f"{c.warning}So if your app does not work, just uninstall it.{c.end}\n"
        )

    # If ensurepip is missing and dependencies exist, install pip manually
    if not can_use_ensurepip and dependencies:
        print("Installing pip in non-system / pip-less Python venv...")
        get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
        # try ensurepip anyway (might fail on Debian/Ubuntu)
        subprocess.run([str(python_in_venv), "-m", "ensurepip", "--upgrade"], check=False)
        # upgrade pip/setuptools/wheel
        subprocess.run([
            str(python_in_venv),
            "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"
        ], check=True)

    # If pip exists, upgrade pip
    if pip_in_venv.exists():
        subprocess.run([str(pip_in_venv), "install", "--upgrade", "pip"], check=True)

    # Install dependencies from requirements files
    if dependencies and pip_in_venv.exists():
        for dependency in dependencies.split(";"):
            dependency = dependency.strip()
            if not dependency:
                continue

            req_file = Path(APP_FILES_DIR) / app_name / dependency
            print("Installing:", req_file)

            subprocess.run([str(pip_in_venv), "install", "-r", str(req_file)], check=True)
