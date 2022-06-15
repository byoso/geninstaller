#! /usr/bin/env python3
# coding: utf-8

"""Example of an embryonic main.py file, this should be included in
a MCV designed program"""

import os
import shutil
from distutils.dir_util import copy_tree

from flamewok import color as c

from geninstaller.helpers import (
    BASE_DIR,
    GI_DIR,
    APP_FILES_DIR,
    APP_DIR,
    DB_FILE,
    no_db,
    gi_db,
    display_list,
    clean_name,
    create_desktop,
    create_dir,
)


def autoinstall():
    """install the empty database"""
    if not os.path.exists(DB_FILE):
        copy_tree(
            BASE_DIR+'/plop/database', GI_DIR)
        print("geninstaller database initialized")


def install(data):

    App = gi_db.model("application")
    app = App.filter(f"name='{data['name']}'")
    if len(app) > 0:
        print(
            f"{c.warning}An application called '{data['name']}'"
            " is already installed, change the current application's"
            f" name, or uninstall the other application first{c.end}."
            )
        return
    if "_" in data['name']:
        print(f"{c.warning}Undersocres are not allowed for an app name{c.end}")
        return
    categories = ""
    for category in data['categories']:
        categories += category + ";"
    applications_files = APP_FILES_DIR + clean_name(data['name'])
    applications = APP_DIR + clean_name(data['name']) + ".desktop"
    if data['terminal']:
        terminal = "true"
    else:
        terminal = "false"
    cleaned_datas = {
        'name': data['name'],
        'exec': data['exec'],
        'comment': data['comment'],
        'terminal': terminal,
        'icon': data['icon'],
        'categories': categories,
        'applications_files': applications_files,
        'applications': applications,
        'base_dir': data['base_dir']

    }
    try:
        App.insert(**cleaned_datas)
        create_dir(cleaned_datas)
        create_desktop(cleaned_datas)
    except:
        print(f"{c.danger}!! Installation issue !!{c.end}")

    print(
        f"{c.success}geninstaller has successfuly installed "
        f"'{data['name']}' on your system{c.end}")
    print("please read the geninstaller's help to know how to use it:")
    print("$ geninstaller -h")


def uninstall(name, *args):
    if no_db():
        return
    App = gi_db.model("application")
    apps = App.filter(f"name='{name}'")
    if len(apps) > 0:
        App.delete(f"id={apps[0].id}")
        print(
            f"{c.success}'{name}' has been successfuly "
            f"removed from your system{c.end}")
    else:
        print(f"'{name}' is not a geninstaller application")
