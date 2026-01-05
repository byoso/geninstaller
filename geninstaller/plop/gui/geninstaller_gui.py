#! /usr/bin/env python3
# -*- coding : utf-8 -*-

from pathlib import Path
import shutil
import subprocess
from typing import Type

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk
from gi.repository import GdkPixbuf

from jsondb import JsonDb, Collection

BASE_DIR = Path.absolute(Path(__file__).parent)
VERSION = "2.1.1"


def get_apps() -> Collection:
    db = JsonDb(
        file=Path("~/.local/share/geninstaller-applications/.geninstaller/geninstaller_db.json").expanduser(),
        autosave=False,
        version="2.0.0",
    )
    apps = db.collection("applications")
    return apps


class AppBox(gtk.HBox):
    def __init__(self) -> None:
        super().__init__()
        self.safety = True

    def uninstall(self, item, pk) -> None:
        if not self.safety:

            app = get_apps().get(pk)
            assert app is not None, "Application not found in database."

            # Delete the application files folder
            subprocess.run("geninstaller uninstall '{}'".format(app['name']), shell=True, check=True)

            # Send notification
            subprocess.run(
                ["notify-send", f"‘{app.get('name')}’ has been removed from your system."],
                check=False
            )
            self.destroy()

    def toggle_safety(self, item) -> None:
        self.safety = not self.safety
        if not self.safety:
            self.uninstall_button.set_opacity(1)
        else:
            self.uninstall_button.set_opacity(0.5)

    def run(self, _event, pk) -> None:

        app = get_apps().get(pk)
        assert app is not None, "Application not found in database."
        desktop_file = app.get('desktop_file')
        assert desktop_file is not None, "Desktop file path not found."
        desktop_file_name = Path(desktop_file).stem
        subprocess.Popen(["gtk-launch", desktop_file_name])


class MainWindow(gtk.Window):
    def __init__(self) -> None:
        gtk.Window.__init__(self)
        # set default filter
        self.filter_by = "name"
        # HeaderBar
        header = gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = f"Geninstaller GUI (v{VERSION})"
        self.set_titlebar(header)
        # refresh button
        refresh_button = gtk.Button()
        refresh_image = gtk.Image.new_from_icon_name("view-refresh", gtk.IconSize.BUTTON)
        refresh_button.set_image(refresh_image)
        refresh_button.set_always_show_image(True)
        header.pack_start(refresh_button)
        refresh_button.connect("clicked", self.refresh)
        # filter field
        self.filter_entry = gtk.SearchEntry()
        self.filter_entry.set_placeholder_text("Filter")
        header.pack_start(self.filter_entry)
        self.filter_entry.connect("search-changed", self.filter_changed)
        # label "by"
        by_label = gtk.Label(label=" by ")
        header.pack_start(by_label)
        # filter_by combobox
        filter_by_combo = gtk.ComboBoxText()
        filter_by_combo.append_text("name")
        filter_by_combo.append_text("category")
        filter_by_combo.set_active(0)
        header.pack_start(filter_by_combo)
        filter_by_combo.connect("changed", self.on_filter_by_changed)


        icon_file = str((BASE_DIR / "geninstaller.png").resolve())
        self.set_default_icon_from_file(icon_file)
        self.set_size_request(800, 600)
        self.set_resizable(True)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.destroy()
        self.scroll = gtk.ScrolledWindow()
        self.add(self.scroll)
        self.viewport = gtk.Viewport()
        self.scroll.add(self.viewport)
        self.main_box = gtk.VBox()
        self.viewport.add(self.main_box)

        self.refresh()

    def on_filter_by_changed(self, combo) -> None:
        self.filter_by = combo.get_active_text()
        # trigger filter update
        self.filter_changed(self.filter_entry)

    def filter_changed(self, entry) -> None:
        if self.filter_by == "name":
            self.filter_by_name(entry)
        if self.filter_by == "category":
            self.filter_by_category(entry)

    def filter_by_name(self, entry) -> None:
        text = entry.get_text().lower()
        for child in self.main_box.get_children():
            app_name = child.item.get_label().lower()
            if text in app_name:
                child.show()
            else:
                child.hide()

    def filter_by_category(self, entry) -> None:
        text = entry.get_text().lower()
        for child in self.main_box.get_children():
            app_categories = ""
            app = get_apps().filter(lambda a: a['name'] == child.item.get_label())[0] if get_apps().filter(lambda a: a['name'] == child.item.get_label()) else None
            if app:
                app_categories = app.get('categories', '').lower()
            if text in app_categories:
                child.show()
            else:
                child.hide()

    def refresh(self, *args) -> None:
        self.filter_entry.set_text("")
        # remove content
        for child in self.main_box.get_children():
            child.destroy()

        # rebuild content
        apps = get_apps().all()
        sorted_apps = sorted(apps, key=lambda x: x['name'].lower())
        for app in sorted_apps:
            icon_path = str(Path(app.get('applications_files', '')) / app.get('icon', ''))

            row = AppBox()
            row.item = gtk.Frame(label=app.get('name'))
            row.item.set_label_align(0.1, 0.5)
            row.item.set_size_request(600, -1)
            row.content = gtk.HBox()
            row.item.add(row.content)

            text = (
                f"- Description: {app.get('description')}\n- Categories: {app.get('categories')}"
                f"\n- Terminal ?: {app.get('terminal')}"
            )
            row.text = gtk.Label(label=text)
            row.text.set_line_wrap(True)
            row.content.pack_start(row.text, False, False, 0)

            try:
                icon_image = GdkPixbuf.Pixbuf.new_from_file(icon_path)
                icon_image = icon_image.scale_simple(
                    64, 64,
                    GdkPixbuf.InterpType.BILINEAR
                )
                image_widget = gtk.Image.new_from_pixbuf(icon_image)
            except Exception:
                image_widget = gtk.Image.new_from_stock(gtk.STOCK_DIALOG_QUESTION, 6)

            row.run_button = gtk.Button()
            row.run_button.set_image(image_widget)
            row.run_button.set_always_show_image(True)

            row.pack_start(row.run_button, False, False, 10)
            row.pack_start(row.item, False, False, 10)

            row.uninstall_button = gtk.Button(label="uninstall")
            row.uninstall_button.get_style_context().add_class("destructive-action")

            row.uninstall_button.set_opacity(0.5)
            row.safety_button = gtk.Button(label="safety")

            row.set_margin_end(20)
            row.uninstall_button.set_margin_bottom(20)
            row.safety_button.set_margin_bottom(20)
            row.content.pack_end(row.uninstall_button, False, False, 10)
            row.content.pack_end(row.safety_button, False, False, 10)

            row.run_button.connect('clicked', row.run, app.get('_id'))
            row.safety_button.connect('clicked', row.toggle_safety)
            row.uninstall_button.connect('clicked', row.uninstall, app.get('_id'))

            self.main_box.pack_start(row, False, False, 5)

        self.main_box.show_all()


window = MainWindow()
window.show_all()
window.connect("delete-event", gtk.main_quit)
gtk.main()
