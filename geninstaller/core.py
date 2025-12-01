#! /usr/bin/env python3
# coding: utf-8

"""The core of geninstaller consist mostly in install and uninstall
applications"""

import os
import subprocess
from pathlib import Path
from dataclasses import asdict

from geninstaller.helpers import (
    APP_FILES_DIR,
    APP_DIR,
    clean_dir_name,
    create_desktop,
    create_dir,
    create_venv,
)
from geninstaller.database import Apps, AppModel
from geninstaller.silly_engine import c


def _install(**kwargs) -> None:
    """Prepares the data before finalization"""
    if not kwargs.get("query_params"):
        print("Install aborted: no query_params provided")
        return
    data = kwargs["query_params"]
    for key in data:
        if key in [
            "categories",
            "options",
        ]:
            data[key] = data[key].strip("\"").split(";")
        else:
            data[key] = data[key].strip("\"")
        if isinstance(data[key], list):
            data[key] = [item.replace("<eq>", "=") for item in data[key]]  # to avoid bash issues
        else:
            data[key] = data[key].replace("<eq>", "=")  # to avoid bash issues
        if key in ["terminal"]:
            if data[key].lower() in ["true", "1", "yes"]:
                data[key] = True
            else:
                data[key] = False

    # transforming datas
    categories = ""
    for category in data['categories']:
        categories += category + ";"
    # directory name:
    applications_files = APP_FILES_DIR + clean_dir_name(data['name'])
    # desktop file name:
    desktop_file = APP_DIR + clean_dir_name(data['name']) + ".desktop"
    python_dependencies = ""
    has_python_dependencies = False
    if data.get('python_dependencies', '') != "":
        has_python_dependencies = True

    for dependence in data.get('python_dependencies', '').split(";"):
        if dependence.strip() == "":
            data['python_dependencies'] = ""
            break
        python_dependencies += APP_FILES_DIR + dependence.strip() + ";"

    db_datas = {
        'name': data['name'].strip(),
        'exec': data['exec'],
        'description': data['description'],
        'terminal': data['terminal'],
        'icon': data['icon'],
        'categories': categories,
        'applications_files': applications_files,
        'desktop_file': desktop_file,
        'python_dependencies': python_dependencies,
    }

    if Apps.filter(lambda x: x['name'] == data['name']):
        print(
            f"{c.warning}Installation aborted: "
            f"an application named '{data['name']}' "
            f"has already been installed with Geninstaller.{c.end}"
            "\nYou can uninstall it and reinstall it if needed."

        )
        return

    all_datas = {
        'base_dir': data['base_dir'],
        'exec_options': data['exec_options'],
        'options': data['options'],
        **db_datas
    }
    # finallization:
    Apps.insert(AppModel(**db_datas))  # validate the data at the same time
    create_dir(all_datas)
    create_desktop(all_datas)

    if has_python_dependencies:
        print("Python dependencies detected, setting up a virtual environment...")
        create_venv(data)

    print(
        f"{c.success}geninstaller has successfuly installed "
        f"'{data['name']}' on your system{c.end}")
    print("please read the geninstaller's help to know how to use it:")
    print("$ geninstaller -h")
    # force update of the desktop database
    subprocess.run(["update-desktop-database", str(Path(desktop_file).parent)])
    # success notification
    os.system(f"notify-send \"'{data['name']}' successfully installed\"")


def uninstall(name: str) -> None:
    apps = Apps.filter(lambda x: x['name'] == name)
    if len(apps) < 1:
        print(f"'{name}' is not a geninstaller application")
        return
    app = AppModel(**apps[0])

    os.system(f"rm {app.desktop_file}")
    os.system(f"rm -rf {app.applications_files}")
    Apps.delete(asdict(app))
    print(
        f"{c.success}'{name}' has been successfuly "
        f"removed from your system{c.end}")
    os.system(f"notify-send \"'{name}' has been removed from your system.\"")
