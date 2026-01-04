#! /usr/bin/env python3

"""The core of geninstaller consist mostly in install and uninstall
applications"""

import os
import subprocess
from pathlib import Path
from dataclasses import asdict
import shutil

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

def file_exists(file: str | Path) -> bool:
    """Verify that all files in the list exist"""
    if not Path(file).exists():
        print(f"{c.warning}Error: file '{file}' does not exist.{c.end}")
        return False
    return True


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
    # pre/post installation scripts
    base_dir = data.get('base_dir')
    if data.get('pre_install_script', '') != "":
        base_file_path = Path(base_dir, data['pre_install_script'])
        if not file_exists(base_file_path):
            print(f"{c.warning}Installation aborted: "
                  f"pre-installation script '{base_file_path}' not found.{c.end}")
            return
        data['pre_install_script'] = str(base_file_path)
    if data.get('post_install_script', '') != "":
        base_file_path = Path(base_dir, data['post_install_script'])
        if not file_exists(base_file_path):
            print(f"{c.warning}Installation aborted: "
                  f"post-installation script '{base_file_path}' not found.{c.end}")
            return
        data['post_install_script'] = str(Path(applications_files, data['post_install_script']))
    if data.get('pre_uninstall_script', '') != "":
        base_file_path = Path(base_dir, data['pre_uninstall_script'])
        if not file_exists(base_file_path):
            print(f"{c.warning}Installation aborted: "
                  f"pre-uninstallation script '{base_file_path}' not found.{c.end}")
            return
        data['pre_uninstall_script'] = str(Path(applications_files, data['pre_uninstall_script']))

    db_data = {
        'name': data['name'].strip(),
        'exec': data['exec'],
        'description': data['description'],
        'terminal': data['terminal'],
        'icon': data['icon'],
        'categories': categories,
        'applications_files': applications_files,
        'desktop_file': desktop_file,
        'python_dependencies': python_dependencies,
        'pre_install_script': data.get('pre_install_script', ''),
        'post_install_script': data.get('post_install_script', ''),
        'pre_uninstall_script': data.get('pre_uninstall_script', '')
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
        **db_data
    }

    # pre-install script execution
    if all_datas.get('pre_install_script', None):
        try:
            subprocess.run(["chmod", "+x", all_datas['pre_install_script']], check=True)
            subprocess.run(all_datas['pre_install_script'], shell=True, check=True)
        except Exception as e:
            print(f"{c.warning}Installation aborted: "
                  f"pre-installation script execution failed: {e}"
                  f"\nInstallation Aborted !{c.end}")
            return
        print(f"{c.success}Pre-installation script executed with success.{c.end}")

    # finallization:
    app_object_in_db = Apps.insert(AppModel(**db_data))  # validate the data at the same time
    create_dir(all_datas)
    create_desktop(all_datas)

    if has_python_dependencies:
        print("Python dependencies detected, setting up a virtual environment...")
        create_venv(data)

    # post-install script execution
    if all_datas.get('post_install_script', None):
        try:
            subprocess.run(["chmod", "+x", all_datas['post_install_script']], check=True)
            subprocess.run(all_datas['post_install_script'], shell=True, check=True)
        except Exception as e:
            print(f"{c.warning}Warning: "
                  f"post-installation script execution failed: {e}"
                  f"\nInstallation Aborted !{c.end}")
            # delete the app from the database and abort installation
            Apps.delete(app_object_in_db)
            shutil.rmtree(applications_files, ignore_errors=True)
            os.remove(desktop_file)
            return
        print(f"{c.success}Post-installation script executed with success.{c.end}")

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

    # pre-uninstall script execution
    if app.pre_uninstall_script:
        try:
            uninstallation_script_success = True
            subprocess.run(["chmod", "+x", app.pre_uninstall_script], check=True)
            subprocess.run(app.pre_uninstall_script, shell=True, check=True)
        except Exception as e:
            uninstallation_script_success = False
        if not uninstallation_script_success:
            print(f"{c.warning}"
                    f"pre-uninstall script execution failed !"
                    f"\nUninstallation continues anyway...{c.end}")
            subprocess.run(
                ["notify-send", f"Warning: pre-uninstall script execution failed for '{name}'."],
                check=False
            )
        else:
            print(f"{c.success}Pre-uninstallation script executed with success.{c.end}")

    os.system(f"rm {app.desktop_file}")
    os.system(f"rm -rf {app.applications_files}")
    Apps.delete(asdict(app))
    print(
        f"{c.success}'{name}' has been successfuly "
        f"removed from your system{c.end}")
    os.system(f"notify-send \"'{name}' has been removed from your system.\"")
