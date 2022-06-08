#! /usr/bin/env python3
# coding: utf-8

"""Example of an embryonic main.py file, this should be included in
a MCV designed program"""

import os
import shutil
from distutils.dir_util import copy_tree

from silly_db.db import DB
from flamewok import color as c

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


def autoinstall():
    """install the empty database"""
    if not os.path.exists(DB_FILE):
        copy_tree(
            BASE_DIR+'/plop/database', GI_DIR)
        print("geninstaller database initialized")


def install(data):
    print("geninstaller installation:")
    print(data)
    db = DB(
        file=DB_FILE,
        base=GI_DIR,
        migrations_dir="None",  # delete with silly-db v 1.1.3
    )
    App = db.model("application")
    app = App.filter(f"name='{data['name']}'")
    if len(app) > 0:
        print(
            f"{c.warning}An application called '{data['name']}'"
            " is already installed, change the current application's"
            f" name, or uninstall the other application first{c.end}."
            )
    categories = ""
    for category in data['categories']:
        categories += category + "/"
    applications_files = APP_FILES_DIR + clean_name(data['name'])
    applications = APP_DIR + clean_name(data['name']) + ".desktop"
    App.insert(
        name=data['name'],
        exec=data['exec'],
        comment=data['comment'],
        terminal=data['terminal'],
        icon=data['icon'],
        categories=categories,
        applications_files=applications_files,
        applications=data['name']+".desktop",
    )
