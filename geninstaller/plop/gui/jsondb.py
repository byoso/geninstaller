#! /usr/bin/env python3

"""
Use a json file as a database, read the docstrings to know more.

e.g.:
from JsonDb import JsonDb

db = JsonDb(
    "data.json",
    autosave=True
    )

Truc = db.collection("Truc")
Machin = db.collection("Machin")

object1 = Truc.insert({"name": "machin", "age": 12})
object2 = Truc.insert({"name": "bidule", "age": 18})

key = object1["_id"]

print(Truc.get(key))

"""
from __future__ import annotations
from pathlib import Path
from dataclasses import is_dataclass, asdict

import json
import os
import uuid

from typing import Any, Callable

WIDTH=80


class JsonDbError(Exception):
    pass


class Version:
    """
    class to handle versions in order to migrate or not the database
    """
    def __init__(self, str_version: str = "0.0.0") -> None:
        list_version = str_version.split(".")
        try:
            self.major = int(list_version[0])
            self.minor = int(list_version[1])
            self.patch = int(list_version[2])
        except (IndexError, ValueError):
            raise JsonDbError("Version: a version must be of the form 'x.x.x' where x are integers (major, minor, patch)")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        return f"Version('{self}')"

    def _as_tuple(self) -> tuple[int, int, int]:
        """Retourne la version sous forme de tuple (major, minor, patch)."""
        return (self.major, self.minor, self.patch)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._as_tuple() == other._as_tuple()

    def __lt__(self, other) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._as_tuple() < other._as_tuple()

    def __gt__(self, other) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._as_tuple() > other._as_tuple()

    def __le__(self, other) -> bool:
        return self == other or self < other

    def __ge__(self, other) -> bool:
        return self == other or self > other


class Item:
    def __init__(self, data, collection, id=None) -> None:
        if "_id" in data:
            self.id = data["_id"]
        self.id = id
        if id is None:
            self.id = str(uuid.uuid4())
        self.collection = collection
        self.data = data
        self.data['_id'] = self.id

    def __repr__(self) -> str:
        return f"<Item - {self.data}>"

    def _autosave(self) -> None:
        if self.collection.database.is_autosaving:
            self.collection.database.save()

    def set(self, *args: tuple) -> Any:
        """args are tuples of (key, value)"""
        try:
            for arg in args:
                if not isinstance(arg, tuple):
                    raise JsonDbError('expected argument type is tuple')
                self.data[arg[0]] = arg[1]
        except JsonDbError as error:
            raise error
        self._autosave()
        return self

    def del_attr(self, *args: str) -> Any:
        for arg in args:
            if not type(arg) is str:
                raise JsonDbError('expected argument type is str')
            if arg in self.data:
                del self.data[arg]
        self._autosave()
        return self

    def update(self, data) -> Any:
        for key in data:
            self.data[key] = data[key]
        self._autosave()
        return self

    def delete(self) -> None:
        del self.collection.data[self.id]
        self._autosave()


class JsonDb:
    """Interface with a json file"""

    def __init__(
            self, file: str | Path="db.json", autosave: bool=False,
            version: str="0.0.0", migrations: dict[str, Callable] | None=None,
            width: int=WIDTH
            ) -> None:
        self.is_autosaving = autosave
        self.file = file
        self.collections = {}
        self.width = width
        self._version = version
        self._migrations = migrations

        if os.path.exists(self.file):
            self.load()

        # check _settings and version
        settings = self.collection("_settings")
        recorded_settings = settings.first()
        if recorded_settings is None:
            settings = self.collection("_settings")
            settings.first_update({"version": self._version})
            self.save()
        elif recorded_settings.get("version", None) is None:
            settings.first_update({"version": self._version})

        # migrations
        recorded_settings = settings.first()
        assert recorded_settings is not None
        recorded_version = recorded_settings.get("version", "0.0.0")
        assert recorded_version is not None
        if self._migrations is not None:
            for migration in self._migrations:
                if Version(recorded_version) < Version(migration) <= Version(self._version):
                    print(f"Migration to v{migration}...")
                    self._migrations[migration](self)
                    settings.first_update({"version": migration})
                    print(f"Successfully upgraded JsonDb to v{migration}")



    def __repr__(self) -> str:
        collection_count = len(self.collections)
        return f"<JsonDb({self.file}, v{self._version}) collections: {collection_count} >"

    def _autosave(self) -> None:
        """Save the database if autosave is enabled"""
        if self.is_autosaving:
            self.save()

    def collection(self, name: str) -> Collection:
        if name not in self.collections:
            self.collections[name] = Collection(name, self)
            self._autosave()
            return self.collections[name]
        else:
            return self.collections[name]

    def save(self) -> None:
        if self.file is None:
            return
        data = {}
        for collection in self.collections:
            data[collection] = {}
            for id in self.collections[collection].data:
                data[collection][id] = self.collections[collection].data[id].data
        try:
            json_str = json.dumps(data, indent=2)
        except (TypeError, ValueError) as e:
            raise JsonDbError(e)
        if not Path(self.file).exists():
            os.makedirs(os.path.dirname(self.file), exist_ok=True)
        with open(self.file, 'w') as file:
            file.write(json_str)

    def load(self) -> None:
        if self.file is None:
            return
        if os.path.exists(self.file):
            try:
                if not Path(self.file).exists():
                    os.makedirs(os.path.dirname(self.file), exist_ok=True)
                with open(self.file, 'r') as file:
                    data = json.load(file)
            except json.JSONDecodeError:
                raise JsonDbError(f"The JsonDb file {self.file} exists but seems to be corrupted.")

            for collection_name in data:
                new_collection = self.collection(collection_name)
                for id in data[collection_name]:
                    new_collection.insert(data[collection_name][id], id)

    def show(self) -> str:
        width = self.width
        collections_count = len(self.collections)
        display = '\n+'+'-'*(width-2) + "+\n"
        display += f"|*-- JsonDb --* file: {self.file} - collections: {collections_count:<13}\n"
        display += f"| {'Collections':40} | {'Item(s)':10}\n"
        display += '+'+'-'*(width-2) + "+\n"

        for collection in self.collections:
            item_count = len(self.collections[collection].data)
            display += f"| {collection:40} | {item_count:10}\n"
        display += '+'+'-'*(width-2) + "+\n"
        return display

    def drop(self, collection_name: str | Collection) -> None:
        """Delete a collection and all its items"""
        if isinstance(collection_name, Collection):
            collection_name = collection_name.name
        if collection_name in self.collections:
            del self.collections[collection_name]
            self._autosave()


class Collection:
    """Collection of dictionnary objects"""
    def __init__(self, name: str, db: JsonDb) -> None:
        self.database = db
        self.name = name
        self.data = {}

    def __repr__(self) -> str:
        return f"<{self.name} - objects in collection: {len(self.database.collection(self.name).data)}>"

    def _autosave(self) -> None:
        if self.database.is_autosaving:
            self.database.save()

    def insert(self, input_data: dict | Any, id=None) -> dict:
        """Add an item to the collection"""
        if is_dataclass(input_data) and not isinstance(input_data, type):
            input_data = asdict(input_data)
        item = Item(input_data, self, id=id)
        self.data[item.id] = item
        self._autosave()
        return item.data

    def update(self, input_data: dict, id=None) -> dict:
        """Update an item in the collection"""
        if input_data.get("_id") is None:
            if id is None:
                raise JsonDbError("The item must have an '_id' key")
            else:
                input_data["_id"] = id
        item = Item(input_data, self, id=input_data["_id"])
        self.data[item.id] = item
        self._autosave()
        return item.data

    def delete(self, input_data: dict, id=None) -> None:
        """Delete an item from the collection
        e.g: self.delete({"_id": "item_id"})
        """
        if id is None:
            if input_data.get('_id') is None:
                raise JsonDbError("The item must have an '_id' key")
            id = input_data.get('_id')
        del self.data[id]
        self._autosave()

    def all(self) -> list[dict]:
        """Returns all the items of the collection"""
        return self.filter(lambda x: True)

    def show(self) -> str:
        """Fancy representation of the collection and its items
        e.g.: print(Collection.show())
        """
        width = self.database.width
        display = '\n+'+'-'*(width-2) + "+\n"
        display += f"|*-- Collection: {self.name} --*\n"
        for id in self.data:
            display += f"| {id} \n"
        display += f"| Total items: {len(self.data)}\n"
        display += '+'+'-'*(width-2) + "+\n"
        return display

    def first(self) -> None | dict:
        """Returns the first item of the collection or None if the collection is empty"""
        if len(self.data) == 0:
            return None
        for key in self.data:
            return self.data[key].data


    def first_update(self, input_data: dict) -> dict | None:
        if len(self.data) == 0:
            new_data = self.insert(input_data)
            return new_data
        for key in self.data:
            new_item = Item(input_data, self, id=key)
            self.data[key] = new_item
            self._autosave()
            return self.data[key].data


    def get(self, key: str) -> dict | None:
        """Get a unique item dict from its id"""
        if key in self.data:
            return self.data[key].data


    def filter(self, query_func: Callable) -> list[dict]:
        """Takes one parameter function that returns a boolean value
        example: queryset = Collection.filter(lambda x: x['age'] > 18)

        returns a list of datas.
        """
        queryset = []
        for id in self.data:
            try:
                if query_func(self.data[id].data):
                    queryset.append(self.data[id].data)
            except KeyError:
                continue
        return queryset


    def filter_delete(self, query_func: Callable) -> None:
        """Takes one parameter function that returns a boolean value
        example: Collection.query_delete(lambda x: x['age'] > 18)
        """
        to_delete = []
        for id in self.data:
            item = self.data[id]
            try:
                if query_func(item.data):
                    to_delete.append(item)
            except KeyError:
                continue
        for item in to_delete:
            item.delete()
        self._autosave()
