#! /usr/bin/env python3
# -*- coding : utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk
from gi.repository import Gdk

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


    def uninstall(self, item, pk):
        app = App.sil.get_id(pk)
        os.system(f"rm {app.applications}")
        os.system(f"rm -rf {app.applications_files}")
        os.system(f"notify-send \"'{app.name}' has been removed from your system.\"")
        App.sil.delete(f"id={app.id}")
        self.destroy()


class MainWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("Geninstaller GUI")
        icon_file = os.path.abspath(
            os.path.join(BASE_DIR, "geninstaller.png"))
        self.set_default_icon_from_file(icon_file)
        self.set_size_request(600, 600)
        self.set_resizable(False)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.destroy()
        self.scroll = gtk.ScrolledWindow()
        self.add(self.scroll)
        self.viewport = gtk.Viewport()
        self.scroll.add(self.viewport)
        self.main_box = gtk.VBox()
        self.viewport.add(self.main_box)


        for app in App.sil.all().order_by("name"):
            row = AppBox()
            row.item = gtk.Frame(label=app.name)
            row.item.set_label_align(0.1, 0.5)
            row.item.set_size_request(550, -1)
            row.content = gtk.HBox()
            row.item.add(row.content)

            text = (
                f"- Description: {app.comment}\n- Categories: {app.categories}"
                f"\n- Terminal ?: {app.terminal}"
                )
            row.text = gtk.Label(label=text)
            row.text.set_line_wrap(True)
            row.content.pack_start(row.text, False, False, 10)
            row.pack_start(row.item, False, False, 10)

            row.button = gtk.Button(label="uninstall")
            row.button.override_background_color(gtk.StateType.NORMAL, Gdk.RGBA(1, 0.5, 0.5))
            row.set_margin_end(20)
            row.button.set_margin_bottom(20)
            row.content.pack_end(row.button, False, False, 10)
            row.button.connect('clicked', row.uninstall, app.id)
            self.main_box.pack_start(row, False, False, 10)


window = MainWindow()
window.show_all()
window.connect("delete-event", gtk.main_quit)
gtk.main()
