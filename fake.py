#! /usr/bin/env python3
# -*- coding : utf-8 -*-

import os

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk as gtk


class MainWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_size_request(200, 150)
        ######
        icon_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'icon.png')
        print(os.path.abspath(os.path.dirname(__file__)))
        # icon_path = '/home/byoso/Bureau/mock_app/icon.png'
        print(icon_path)
        self.set_icon_from_file(icon_path)

        ###### supprimer home/byoso/icon.png
        scroll = gtk.ScrolledWindow()
        self.add(scroll)
        viewport = gtk.Viewport()
        scroll.add(viewport)
        box = gtk.VBox()
        viewport.add(box)
        it1 = gtk.Label("1")
        box.pack_start(it1, False, False, 10)
        it2 = gtk.Button.new_from_stock(gtk.STOCK_NO)
        box.pack_start(it2, False, False, 10)
        it3 = gtk.Label("truc")
        box.pack_start(it3, False, False, 10)
        it4 = gtk.Label("machin")
        box.pack_start(it4, False, False, 10)
        it5 = gtk.Label("bidule")
        box.pack_start(it5, False, False, 10)


window = MainWindow()
window.show_all()
window.connect("delete-event", gtk.main_quit)
gtk.main()
