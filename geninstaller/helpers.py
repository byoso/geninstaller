import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

GI_DIR = os.path.expanduser(
    "~/.local/share/applications-files/.geninstaller/")
APP_FILES_DIR = os.path.expanduser(
    "~/.local/share/applications-files/")
APP_DIR = os.path.expanduser(
    "~/.local/share/applications/")
DB_FILE = os.path.expanduser(
    "~/.local/share/applications-files/.geninstaller/gi_db.sqlite3")


def no_db():
    """check if the database already exists or not"""
    if not os.path.exists(DB_FILE):
        print("geninstaller's database has not been initialized.")
        return True
    else:
        return False


def display_list(apps):
    if len(apps) == 0:
        print("No result found")
        return
    print("="*119)
    print(f"{'Application':<45}|{'terminal ? ':^12}|{'Categories':<60}|")
    print("="*119 + "|")
    for app in apps:
        print(
            f"{app.name:<119}|\n"
            f"{app.comment:<45}|"
            f"{app.terminal:^12}|{app.categories:<60}|")
        print("_"*119 + "|")


def clean_name(name):
    cleaner = name.strip()
    dir_name = ""
    for letter in cleaner:
        if letter in list(" ;,/"):
            dir_name += "_"
        else:
            dir_name += letter
    return dir_name



def create_desktop(data):
    pass


def create_dir(data):
    pass