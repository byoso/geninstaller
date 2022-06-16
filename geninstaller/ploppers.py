"""
This module handles the 'plop' command when used to copy an already
existing file (in the package) to the user's cwd.
"""
import os
import shutil

from geninstaller.helpers import set_executable

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def plop_installer():
    "plop's the installer in your cwd"
    file = os.path.join(BASE_DIR, "plop/installer/installer")
    cwd = os.getcwd()
    shutil.copy(file, cwd)
    set_executable(os.path.join(cwd, 'installer'))
    print(f"installer plopped in {cwd}")
