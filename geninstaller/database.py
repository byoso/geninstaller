#! /usr/bin/env python3

from pathlib import Path
from datetime import datetime

from dataclasses import dataclass

from geninstaller.silly_engine.jsondb import JsonDb, Collection
from geninstaller.migrations.migrations_2_1 import mig_2_1_0

BASE_DIR_PATH = Path(__file__).parent.resolve()
GI_DIR_PATH = Path.home() / ".local" / "share" / "geninstaller-applications" / ".geninstaller"
DB_FILE_PATH = GI_DIR_PATH / "geninstaller_db.json"


@dataclass
class AppModel:
    name: str
    exec: str
    icon: str
    desktop_file: str
    applications_files: str
    date: str = ""
    terminal: bool = False
    categories: str = ""
    version: str = ""
    description: str = ""
    python_dependencies: str = ""
    pre_install_script: str = ""
    post_install_script: str = ""
    pre_uninstall_script: str = ""
    base_dir: str = ""
    exec_options: str = ""
    options: str = ""
    _id: str = ""

    def __post_init__(self) -> None:
        if not self.date:
            self.date = str(datetime.now())


gdb = JsonDb(DB_FILE_PATH, autosave=True, version="2.1.0", migrations={
    "2.1.0": mig_2_1_0
})
Settings: Collection = gdb.collection("_settings")
Apps : Collection = gdb.collection("applications")


if __name__ == "__main__":
    app = AppModel(name="TestApp",
                   exec="/usr/bin/testapp",
                   icon="/usr/share/icons/testapp.png",
                   desktop_file="/home/user/.local/share/applications/testapp.desktop",
                   applications_files="/home/user/.local/share/geninstaller/apps/testapp/")
    # Apps.insert(app)
    print(Apps)
    # gdb.drop(Apps)
    print(Settings.first())
    print(Apps)
