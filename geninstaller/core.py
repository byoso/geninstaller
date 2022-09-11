#! /usr/bin/env python3
# coding: utf-8

"""The core of geninstaller consist mostly in install and uninstall
applications"""

import os

from flamewok import color as c

from geninstaller.helpers import (
    APP_FILES_DIR,
    APP_DIR,
    get_db,
    clean_dir_name,
    create_desktop,
    create_dir,
    valid_for_installation,
)


def install(data):
    """Prepares the data before finalization"""
    # first, some data check
    valid_for_installation(data)

    # transforming datas
    categories = ""
    for category in data['categories']:
        categories += category + ";"
    # directory name:
    applications_files = APP_FILES_DIR + clean_dir_name(data['name'])
    # desktop file name:
    applications = APP_DIR + clean_dir_name(data['name']) + ".desktop"
    if data['terminal']:
        terminal = "true"
    else:
        terminal = "false"

    db_datas = {
        'name': data['name'].strip(),
        'exec': data['exec'],
        'comment': data['comment'],
        'terminal': terminal,
        'icon': data['icon'],
        'categories': categories,
        'applications_files': applications_files,
        'applications': applications,

    }
    all_datas = {
        'base_dir': data['base_dir'],
        'exec_options': data['exec_options'],
        'options': data['options'],
        **db_datas
    }
    # finallization:
    gi_db = get_db()
    App = gi_db.model("application")
    App.sil.insert(**db_datas)
    create_dir(all_datas)
    create_desktop(all_datas)

    print(
        f"{c.success}geninstaller has successfuly installed "
        f"'{data['name']}' on your system{c.end}")
    print("please read the geninstaller's help to know how to use it:")
    print("$ geninstaller -h")
    os.system(f"notify-send \"'{data['name']}' successfully installed\"")


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
    apps = App.sil.filter(f"name='{name}'")
    if len(apps) < 1:
        print(f"'{name}' is not a geninstaller application")
        return
    app = App.sil.get_id(apps[0].id)

    os.system(f"rm {app.applications}")
    os.system(f"rm -rf {app.applications_files}")
    App.sil.delete(f"id={app.id}")
    print(
        f"{c.success}'{name}' has been successfuly "
        f"removed from your system{c.end}")
    os.system(f"notify-send \"'{name}' has been removed from your system.\"")
