#! /usr/bin/env python3
# coding: utf-8
import os

from flamewok.cli import cli
from silly_db.db import DB

from geninstaller import __version__
from geninstaller import core
from geninstaller import ploppers
from geninstaller.helpers import (
    BASE_DIR,
    GI_DIR,
    APP_FILES_DIR,
    APP_DIR,
    DB_FILE,
    no_db,
    display_list,
    clean_name,
)


def list(*args):
    if no_db():
        return
    db = DB(
        file=DB_FILE,
        base=GI_DIR,
        # migrations_dir="None",  # delete with silly-db v 1.1.4
    )
    App = db.model("application")
    apps = App.all()
    display_list(apps)


def open_geninstaller_dir(*args):
    """Directory where the database is installed localy"""
    if no_db():
        return
    os.system(f"xdg-open {GI_DIR}")


def open_apps_dir(*args):
    if no_db():
        return
    os.system(f"xdg-open {APP_FILES_DIR}")


def search(name, *args):
    name = name
    if no_db():
        return
    db = DB(
        file=DB_FILE,
        base=GI_DIR,
        # migrations_dir="None",  # delete with silly-db v 1.1.3
    )
    apps = db.select(f"* FROM application WHERE name LIKE '%{name}%'")
    display_list(apps)


def cmd():
    routes = [
        "HELP",
        ("-h", cli.help, "display this help"),
        ("--help", cli.help, "idem"),
        ("", cli.help, "idem"),
        "ACTIONS",
        ('list', list, "list the applications installed with geninstaller"),
        ('search <name>', search,
            "search an application with an approximate name"),
        ('uninstall <name>', core.uninstall, (
            "uninstall an application with its exact name, "
            "use '' if the 'app name' contains a blank space")),
        "OPEN DIRECTORIES",
        ('open', open_apps_dir,
            "open the applications installation directory"),
        ('open database', open_geninstaller_dir,
            "open the geninstaller's database directory"),
        "FOR DEVELOPPERS",
        ('plop installer', ploppers.plop_installer,
            "provides a ready-to-complete-and-use "
            "'installer' template into your current working directory"),
        "_"*78,
        "ABOUT",
        "program: geninstaller",
        f"version: {__version__}",
        "home page : https://github.com/byoso/geninstaller",

    ]
    cli.route(*routes)


if __name__ == "__main__":
    cmd()