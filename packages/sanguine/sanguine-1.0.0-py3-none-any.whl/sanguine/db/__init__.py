import os

import appdirs
from peewee import SqliteDatabase

import sanguine.meta as meta

app_dir = appdirs.user_data_dir(meta.name)
os.makedirs(app_dir, exist_ok=True)
db_file = os.path.join(app_dir, "db.db")
db = SqliteDatabase(db_file)
