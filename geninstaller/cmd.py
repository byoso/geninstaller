#! /usr/bin/env python3
# coding: utf-8
import os

from geninstaller import __version__
from geninstaller import core
from geninstaller import ploppers
from geninstaller.plop.gui.gui_installer import install_gui
from geninstaller.helpers import (
    GI_DIR,
    APP_FILES_DIR,
    display_list,
)
from geninstaller.silly_engine import Router, RouterError
from geninstaller.database import Apps, AppModel


def list(*args) -> None:
    display_list(Apps.all())


def open_geninstaller_dir(*args) -> None:
    """Directory where the database is installed localy"""
    os.system(f"xdg-open {GI_DIR}")


def open_apps_dir(*args) -> None:
    os.system(f"xdg-open {APP_FILES_DIR}")


def search(name=None, *args) -> None:
    name = name
    if name is None:
        return list()
    apps = Apps.filter(lambda x: name.lower() in x['name'].lower())
    display_list(apps)

def get_version() -> str:
    print(__version__)
    return __version__


def cmd() -> None:

    router = Router(name="geninstaller", width=80)

    routes = [
        "HELP",
        (["", "-h", "--help"], router.display_help, "show this help\n"),
        "ACTIONS",
        ('list', list, "list the apps installed with geninstaller"),
        ('search <name>', search,
            "search an application with an approximate name"),
        ('uninstall <name>', core.uninstall, (
            "uninstall an application with its exact name, "
            "  use '' if the 'app name' contains a blank space")),
        "GUI",
        ('gui', install_gui, "Installs the geninstaller's graphical interface on your system\n"),
        "OPEN DIRECTORIES",
        ('open', open_apps_dir,
            "open the applications installation directory"),
        ('open database', open_geninstaller_dir,
            "open the geninstaller's database directory\n"),
        "FOR DEVELOPPERS",
        ('plop installer', ploppers.plop_installer,
            "provides a ready-to-complete-and-use "
            "'installer' template into your current working directory"),
        ("version", get_version, "display the version of geninstaller\n"),
        "_"*78,
        "RUNNNER",
        ("_install", core._install, "used by the 'installer' scripts only, do not use this route manually"),
        "_"*78,
        "ABOUT",
        "program: geninstaller",
        f"version: {__version__}",
        "home page : https://github.com/byoso/geninstaller",

    ]

    router.add_routes(routes)
    try:
        router.query()
    except RouterError as e:
        print(f"Router error: {e}")



if __name__ == "__main__":
    cmd()
