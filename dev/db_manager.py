#! /usr/bin/env python3
# coding: utf-8

"""Example of an embryonic main.py file, this should be included in
a MCV designed program"""

import os
from silly_db.db import DB

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

db = DB(
    base=BASE_DIR,
    file="database/gi_db.sqlite3",
    migrations_dir="migrations")
# db.migrate_all()
db.export()
