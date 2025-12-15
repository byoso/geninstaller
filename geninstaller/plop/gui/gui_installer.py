#! /usr/bin/env python3
# coding: utf-8

"""
Installs Geninstaller-gui
"""

import os

from geninstaller.config import DEV_MODE


NAME = "geninstaller_gui"
DESCRIPTION = "Uninstall with only one click your geninstaller applications"
EXECUTABLE = "geninstaller_gui.py"
ICON = "geninstaller.png"
TERMINAL = False

CATEGORIES = [
    # "AudioVideo",
    # "Audio",
    # "Video",
    # "Development",
    # "Education",
    # "Game",
    # "Graphics",
    # "Network",
    # "Office",
    # "Science",
    # "Settings",
    "System",
    # "Utility",
]

# ADDITIONAL OPTIONS
exec_options = ""
options = [
]


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

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


def install_gui() -> None:

    query_params = f'?name="{NAME}"+exec="{EXECUTABLE}"+description="{DESCRIPTION}"+' \
        f'terminal="{TERMINAL}"+icon="{ICON}"+categories="{";".join(CATEGORIES)}"+' \
        f'base_dir="{BASE_DIR}"+exec_options="{exec_options}"+options="{";".join(options)}"+' \
        'pre_install_file=""+post_install_file=""+' \
        'pre_uninstall_file=""+post_uninstall_file=""+' \
        'python_dependencies=""'
    import subprocess

    if DEV_MODE:
        subprocess.run(["python", "-m", "geninstaller.cmd", "_install", query_params], check=True)
    else:
        subprocess.run(["geninstaller", "_install", query_params], check=True)
