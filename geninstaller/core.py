#! /usr/bin/env python3
# coding: utf-8

"""The core of geninstaller consist mostly in install and uninstall
applications"""

import os
import shutil

from flamewok import color as c

from geninstaller.helpers import (
    BASE_DIR,
    GI_DIR,
    APP_FILES_DIR,
    APP_DIR,
    DB_FILE,
    get_db,
    clean_name,
    create_desktop,
    create_dir,
)


def install(data):
    """Prepares the data before finalization"""
    # first, some data check
    gi_db = get_db()
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
    if type(data['terminal']) != bool:
        print(f"{c.warning}The 'TERMINAL' value must be a boolean{c.end}")
        return

    categories = ""
    for category in data['categories']:
        categories += category + "/"
    applications_files = APP_FILES_DIR + clean_name(data['name'])
    applications = APP_DIR + clean_name(data['name']) + ".desktop"
    if data['terminal']:
        terminal = "true"
    else:
        terminal = "false"

    db_datas = {
        'name': data['name'],
        'exec': data['exec'],
        'comment': data['comment'],
        'terminal': terminal,
        'icon': data['icon'],
        'categories': categories,
        'applications_files': applications_files,
        'applications': applications,

    }
    cleaned_datas = {
        'base_dir': data['base_dir'],
        **db_datas
    }
    # finallization:
    App.insert(**db_datas)
    create_dir(cleaned_datas)
    create_desktop(cleaned_datas)

    print(
        f"{c.success}geninstaller has successfuly installed "
        f"'{data['name']}' on your system{c.end}")
    print("please read the geninstaller's help to know how to use it:")
    print("$ geninstaller -h")


def uninstall(name, *args):
    if len(args) > 0:
        print(
            f"{c.warning}To many arguments given{c.end}\n"
            "If the name of your app contains multiple words, \n"
            "write it with quotes: 'your app name'"
            )
        return
    gi_db = get_db()
    App = gi_db.model("application")
    apps = App.filter(f"name='{name}'")
    if len(apps) < 1:
        print(f"'{name}' is not a geninstaller application")
        return
    app = App.get_id(apps[0].id)

    os.system(f"rm {app.applications}")
    os.system(f"rm -rf {app.applications_files}")
    App.delete(f"id={app.id}")
    print(
        f"{c.success}'{name}' has been successfuly "
        f"removed from your system{c.end}")
