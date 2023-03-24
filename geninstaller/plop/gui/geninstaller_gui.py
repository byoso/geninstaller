#! /usr/bin/env python3
# -*- coding : utf-8 -*-

import os
import gi
from PIL import Image
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk
from gi.repository import Gdk, GdkPixbuf

from silly_db.db import DB

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database initialized here
db = DB(
    file="~/.local/share/applications-files/.geninstaller/gi_db.sqlite3",
    migrations_dir="~/.local/share/applications-files/.geninstaller/migrations",
    )
db.migrate_all()

App = db.model("application")


class AppBox(gtk.HBox):
    def __init__(self):
        super().__init__()
        self.safety = True

    def uninstall(self, item, pk):
        if not self.safety:
            app = App.sil.get_id(pk)
            os.system(f"rm {app.applications}")
            os.system(f"rm -rf {app.applications_files}")
            os.system(
                f"notify-send \"'{app.name}' has been removed"
                " from your system.\""
            )
            App.sil.delete(f"id={app.id}")
            self.destroy()

    def toggle_sefaty(self, item):
        self.safety = not self.safety
        if not self.safety:
            self.button.set_opacity(1)
        else:
            self.button.set_opacity(0.5)


class MainWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("Geninstaller GUI")
        icon_file = os.path.abspath(
            os.path.join(BASE_DIR, "geninstaller.png"))
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

        for app in App.sil.all().order_by("name"):
            icon_path = os.path.join(app.applications_files, app.icon)

            row = AppBox()
            row.item = gtk.Frame(label=app.name)
            row.item.set_label_align(0.1, 0.5)
            row.item.set_size_request(600, -1)
            row.content = gtk.HBox()
            row.item.add(row.content)

            text = (
                f"- Description: {app.comment}\n- Categories: {app.categories}"
                f"\n- Terminal ?: {app.terminal}"
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
                icon = gtk.Image.new_from_pixbuf(icon_image)
            except:
                icon = gtk.Image.new_from_stock(gtk.STOCK_DIALOG_QUESTION, 6)

            row.pack_start(icon, False, False, 10)
            row.pack_start(row.item, False, False, 10)

            row.button = gtk.Button(label="uninstall")
            row.button.get_style_context().add_class("destructive-action")

            row.button.set_opacity(0.5)
            row.safety_button = gtk.Button(label="safety")

            row.set_margin_end(20)
            row.button.set_margin_bottom(20)
            row.safety_button.set_margin_bottom(20)
            row.content.pack_end(row.button, False, False, 10)
            row.content.pack_end(row.safety_button, False, False, 10)

            row.safety_button.connect('clicked', row.toggle_sefaty)
            row.button.connect('clicked', row.uninstall, app.id)
            self.main_box.pack_start(row, False, False, 5)


window = MainWindow()
window.show_all()
window.connect("delete-event", gtk.main_quit)
gtk.main()
