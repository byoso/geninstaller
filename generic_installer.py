#! /usr/bin/env python3
# coding: utf-8

import os
import subprocess
import stat

## Dependencies check
import pkg_resources
dependencies = [
    'flamewok>=1.0.2',
]
try:
    pkg_resources.require(dependencies)
except pkg_resources.DistributionNotFound:
    os.system('pip install flamewok')


import flamewok
from flamewok import (
    Menu,
    clear,
    Form,
    check_type,
    color as c,
)

DEV_MODE = False

categories = {
    "1": "AudioVideo",
    "2": "Audio",
    "3": "Video",
    "4": "Development",
    "5": "Education",
    "6": "Game",
    "7": "Graphics",
    "8": "Network",
    "9": "Office",
    "10": "Settings",
    "11": "Utility",
}

help_content = """
THIS program...
...will help you to create quickly a .desktop file, for an
application that comes without a .desktop file, typicaly appimages
applications, or any executable you want to integrate in your
OS, without the need of any specific knowlege.

1. Copy / Paste...
...your application where you want it to be (and to stay).
The standard way is to create a folder in '/opt', or in
'~/.local/share', put inside the app and a cool icon of your choice.

2. In this program...
select "create launcher",  and fill the few asked fields. You'll be asked
for the categories you whant your app to appear in (optional).
At the end, you'll be asked if you whant your launcher on your desktop,
in your current working directory, or integrate the launcher in your
OS. This last one makes a simple copy in ~/.local/share/applications,
then the app will only appear in the menus for the current user.

"""

main_menu = Menu(box_size = 30, line_length = 90)
way_choice_menu = Menu(box_size = 30, line_length = 90)
integration_menu = Menu(box_size = 30, line_length = 90)
categories_menu = Menu(box_size = 30, line_length = 90)
new_one_menu = Menu(box_size = 30, line_length = 90)

name_form = Form([
    ("name", "Enter the name that your OS will use as application name:",
        lambda x: x != "", "not optionnal !"),
])

desktop_form = Form([
    ("comment", "The comment displayed by your OS (optionnal)"),
    ("exec", 'Enter the absolute path to the executable (drag n drop)',
        lambda x: x != "", "not optionnal !"),
    ("icon", "Enter the absolute path of your icon (drag n drop, optionnal)"),
    ("terminal", "The app is displayed in a terminal ? (y/n, default is no)"),
])

categories_form = Form([
    ("name", "Select the id of a category (empty to cancel)",
        lambda x: x == "" or (
            check_type(x, int) and int(x) > 0 and int(x) <= len(categories)
            )),
])
manual_category_form = Form([
    ("name", (
        "Enter your category (be sure you know what you're doing," +
        " leave empty to cancel):"
        )),
])


class Main:
    def __init__(self):
        self.selected_cat = []
        self.message = ""
        self.data = None
        self.choice = ""
        # Menus building
        main_menu.add_boxes([
            ("1", "help", self.help),
            ("2", "create laucher", self.way_choice_menu),
            ("x", "quit", quit),
            ])
        way_choice_menu.add_boxes([
            "Choose where do you whant to create the launcher\n",
            ("1", "Working directory", self.choice_cwd),
            ("2", "Desktop", self.choice_cwd),
            ("3", "Integration in the menu", self.choice_integrate),
            ("x", "quit", quit),
        ])
        integration_menu.add_boxes([
            "\nCOPY YOUR APPLICATION IN THIS OPENING DIRECTORY\n",
            ("0", "no, cancel", quit),
            ("+", "ok, done", self.end_path_integration),
        ])
        categories_menu.add_boxes([
            ("1", "add a category", self.categories_form),
            ("2", "reset selection", self.reset_selected_categories),
            ("3", "manual entry", self.manual_category),
            ("+", "done", self.end_categories),
        ])
        new_one_menu.add_boxes([
            "Add the launcher to ...\n",
            ("1", "my Working directory", self.path_cwd),
            ("2", "my Desktop", self.path_desktop),
            ("x", "quit", quit),
        ])

        if not DEV_MODE:
            clear()
        print("-- Generic Installer / launcher maker --\n")

        main_menu.ask()

    def help(self):
        if not DEV_MODE:
            clear()
        print(help_content)
        main_menu.ask()

    def way_choice_menu(self):
        clear()
        way_choice_menu.ask()

    def choice_cwd(self):
        """both for cwd and desktop choice"""
        self.choice = "no_integration"
        response = name_form.ask()
        self.data = desktop_form.ask()
        self.data.name = response.name
        self.categories_menu()

    def choice_integrate(self):
        self.choice = "integration"
        self.name = name_form.ask().name
        self.categories_menu()

    def choice_integrate2(self):
        self.data = desktop_form.ask()
        self.data.name = self.name
        self.message = f"file created at {self.path}\n"
        self.create_file(self.data, self.selected_cat, self.path)
        self.finalize()

    def categories_menu(self):
        if not DEV_MODE:
            clear()
        print("-- Categories selection --")
        for id, cat in categories.items():
            print(f"{id:<10}{cat}")
        if len(self.selected_cat) > 0:
            print("\nYour selection:")
            for cat in self.selected_cat:
                print(f"- {cat}")
        print("\n")
        categories_menu.ask()

    # def integration_menu(self):
    #     integration_menu.ask()

    def reset_selected_categories(self):
        self.selected_cat = []
        self.categories_menu()

    def manual_category(self):
        cat = manual_category_form.ask()
        if cat.name != "":
            self.selected_cat.append(cat.name.strip())
        self.categories_menu()

    def categories_form(self):
        """asked for manual category entry"""
        selection = categories_form.ask()
        if selection.name != "" and categories[selection.name] \
                not in self.selected_cat:
            self.selected_cat.append(categories[selection.name])
        self.categories_menu()

    def path_cwd(self):
        path = os.getcwd()+"/"
        self.create_file(self.data, self.selected_cat, path)

    def path_desktop(self):
        path = subprocess.check_output(
            ['xdg-user-dir', 'DESKTOP']).decode('utf-8')[:-1]+"/"
        self.message = f"file created at {path}\n"
        self.create_file(self.data, self.selected_cat, path)

    def path_integration(self, name):
        # create dir:
        dir_name = name.replace(" ", "_")
        # os.system('mkdir ~/.local/share/applications-files')
        os.system(f'mkdir -p ~/.local/share/applications-files/{dir_name}')
        os.system(
            'touch ~/.local/share/applications-files/'
            f'{dir_name}/COPY_HERE'
            )
        os.system(
            f'xdg-open ~/.local/share/applications-files/{dir_name}')
        self.path = subprocess.check_output(
                ['xdg-user-dir']).decode('utf-8')[:-1]
        self.path += "/.local/share/applications/"

        integration_menu.ask()

    def end_path_integration(self):
        self.choice_integrate2()

    def create_file(self, data, categories, path):
        self.data.exec = self.data.exec.strip().strip("'").replace(" ", "\\ ")
        self.data.icon = self.data.icon.strip().strip("'")
        categories_line = ""
        for cat in categories:
            categories_line += f"{cat};"

        content = str(
            "[Desktop Entry]\n"
            f"Name={data.name}\n"
            f"Exec={data.exec}\n"
            f"Comment={data.comment}\n"
            f"Terminal={data.terminal}\n"
            f"Icon={data.icon}\n"
            "Type=Application\n"
            f"Categories={categories_line}\n"
        )
        file_path = f"{path}{data.name}"
        try:

            with open(f"{file_path}.desktop", "w") as file:
                file.write(content)
            st = os.stat(f"{file_path}.desktop")
            os.chmod(
                f"{file_path}.desktop",
                st.st_mode | stat.S_IEXEC | stat.S_IXUSR |
                stat.S_IXGRP | stat.S_IXOTH
                )

            self.message = f"{c.success}FILE CREATED{c.end} at {path}\n"

        except PermissionError:
            self.message = (
                f"{c.warning}PERMISSION DENIED{c.end}"
                "\nYou should create "
                "the file on your desktop, and then copy it manualy "
                "to the intended directory."
            )
        self.finalize()

    def end_categories(self):
        print("=== end cat")
        if self.choice == "integration":
            self.path_integration(self.name)
            self.integration_menu.ask()
        else:
            self.finalize()

    def finalize(self):
        # set 'terminal' value
        if self.data.terminal not in ('true', 'false'):
            if self.data.terminal.lower().startswith('y'):
                self.data.terminal = "true"
            else:
                self.data.terminal = "false"

        if not DEV_MODE:
            clear()
        print(self.message)
        print("LAST CHECK:\n")
        print(
            f"Name: {self.data.name}\nComment: {self.data.comment}\n"
            f"Executable: {self.data.exec}\nIcon: {self.data.icon}\n"
            f"Terminal: {self.data.terminal}\n")
        if (self.selected_cat):
            print("Selected categories: ")
            for cat in self.selected_cat:
                print(cat)
        print("\n")
        cwd = os.getcwd()
        print(f"Your working directory is : {cwd}\n")

        new_one_menu.ask()


if __name__ == "__main__":
    try:
        Main()
    except KeyboardInterrupt:
        pass
