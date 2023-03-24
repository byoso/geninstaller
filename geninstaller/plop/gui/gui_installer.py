#! /usr/bin/env python3
# coding: utf-8

"""
Installs Geninstaller-gui
"""

import os

from geninstaller import core

NAME = "Geninstaller gui"
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

datas = {
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


def install_gui():
    core.install(datas)
