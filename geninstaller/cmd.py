#! /usr/bin/env python3
# coding: utf-8
import os

from flamewok.cli import cli
from silly_db.db import DB

from geninstaller import __version__
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
        migrations_dir="None",  # delete with silly-db v 1.1.3
    )
    App = db.model("application")
    apps = App.all()
    display_list(apps)


def open_geninstaller_dir(*args):
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
        migrations_dir="None",  # delete with silly-db v 1.1.3
    )
    apps = db.select(f"* FROM application WHERE name LIKE '%{name}%'")
    display_list(apps)


def uninstall(*args):
    # name = name
    print(args)
    # if no_db():
    #     return
    # db = DB(
    #     file=DB_FILE,
    #     base=GI_DIR,
    #     migrations_dir="None",  # delete with silly-db v 1.1.3
    # )
    # App = db.model("application")
    # apps = App.filter(f"name='{name}'")
    # if len(apps) > 1:
    #     apps[0].delete()



def cmd():
    routes = [
        "program: Geninstaller",
        f"version: {__version__}",
        "HELP",
        ("-h", cli.help, "display this help"),
        "ACTIONS",
        ('uninstall <name>', uninstall, "uninstall an application with its exact name"),
        ('list', list, "list the installed applications"),
        ('search <name>', search,
            "search an application with an approximate name"),
        "OPEN DIRECTORIES",
        ('open', open_apps_dir,
            "open the applications installation directory"),
        ('open database', open_geninstaller_dir,
            "open the geninstaller's database directory"),
    ]
    cli.route(*routes)


if __name__ == "__main__":
    cmd()