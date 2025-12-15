#! /usr/bin/env python3
# -*- coding : utf-8 -*-

from pathlib import Path
import shutil
import subprocess

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk
from gi.repository import GdkPixbuf

from jsondb import JsonDb, Collection

BASE_DIR = Path.absolute(Path(__file__).parent)


def get_apps() -> Collection:
    db = JsonDb(
        file=Path("~/.local/share/geninstaller-applications/.geninstaller/geninstaller_db.json").expanduser(),
        autosave=True,
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

            # delete the file .desktop
            desktop_file = Path(app["desktop_file"])
            desktop_file.unlink(missing_ok=True)

            # Delete the application files folder
            applications_files = Path(app['applications_files'])
            shutil.rmtree(applications_files, ignore_errors=True)

            # Remove from database
            get_apps().delete({"_id": app.get('_id')})

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
        # HeaderBar
        header = gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Geninstaller GUI (v2)"
        self.set_titlebar(header)
        # refresh button
        refresh_button = gtk.Button()
        refresh_image = gtk.Image.new_from_icon_name("view-refresh", gtk.IconSize.BUTTON)
        refresh_button.set_image(refresh_image)
        refresh_button.set_always_show_image(True)
        header.pack_start(refresh_button)
        refresh_button.connect("clicked", self.refresh)

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

    def refresh(self, *args) -> None:
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
