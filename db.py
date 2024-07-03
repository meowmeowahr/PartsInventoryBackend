import sqlite3
import uuid
from loguru import logger
import json
import pprint
import time
import sys


class BaseDatabase:
    def __init__(self):
        # Connect to DB and create a cursor
        self.sqlite_connection = sqlite3.connect('sql.db')
        logger.success("Database initialized")
        logger.info(f"SQLite version: {self.get_sqlite_version()}")

        self.create_tables()

    def get_sqlite_version(self):
        query = 'select sqlite_version();'
        cursor = self.sqlite_connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

        return result[0][0]

    @property
    def total_changes(self) -> int:
        return self.sqlite_connection.total_changes

    def create_tables(self):
        pass

    def end(self):
        if self.sqlite_connection:
            self.sqlite_connection.close()


class SorterIdInvalidException(BaseException):
    pass


class PartSorter(BaseDatabase):
    def create_tables(self):
        with self.sqlite_connection:
            self.sqlite_connection.execute("""CREATE TABLE IF NOT EXISTS locations (
                                                                    id TEXT PRIMARY KEY, 
                                                                    name TEXT NOT NULL, 
                                                                    icon TEXT NOT NULL, 
                                                                    tags TEXT,
                                                                    attrs TEXT NOT NULL
                                                                    )""")
            self.sqlite_connection.execute("""CREATE TABLE IF NOT EXISTS sorters (
                                                                    id TEXT PRIMARY KEY,
                                                                    location TEXT NOT NULL,
                                                                    name TEXT NOT NULL,
                                                                    icon TEXT NOT NULL,
                                                                    tags TEXT,
                                                                    attrs TEXT NOT NULL
                                                                    )""")

    def create_location(self, uid: str, name: str, icon: str, tags: str, attributes: dict):
        if uid in self.get_location_ids():
            raise SorterIdInvalidException(f"Another location with id: {uid} already exists")
        with self.sqlite_connection:
            cursor = self.sqlite_connection.cursor()
            cursor.execute("INSERT INTO locations (id,name,icon,tags,attrs) VALUES(?,?,?,?,?)",
                           (uid, name, icon, tags, json.dumps(attributes)))
            cursor.close()
        logger.info(f"Created new location with id: {uid}")

    def delete_location(self, uid: str):
        if uid not in self.get_location_ids():
            raise SorterIdInvalidException(f"Location with id: {uid} does not exist")
        with self.sqlite_connection:
            cursor = self.sqlite_connection.cursor()
            cursor.execute("DELETE FROM locations WHERE id=?",
                           (uid,))

    def get_locations(self) -> list:
        try:
            cursor = self.sqlite_connection.cursor()
            cursor.execute("SELECT * FROM locations")
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in rows]
            for row in rows:
                if 'attrs' in row and isinstance(row['attrs'], str):
                    row['attrs'] = json.loads(row['attrs'])

            return rows
        except sqlite3.Error as e:
            logger.error(f"Experienced error getting locations, returning empty list: {repr(e)}")
            return []

    def get_location_ids(self) -> list:
        try:
            cursor = self.sqlite_connection.cursor()
            cursor.execute("SELECT id FROM locations")
            rows = cursor.fetchall()
            rows = [row[0] for row in rows]

            return rows
        except sqlite3.Error as e:
            logger.error(f"Experienced error getting locations, returning empty list: {repr(e)}")
            return []

    def update_location(self, uid: str, name: str = None, icon: str = None, tags: str = None, attributes: dict = None):
        with self.sqlite_connection:
            cursor = self.sqlite_connection.cursor()
            updates = []
            params = []

            if name is not None:
                updates.append("name = ?")
                params.append(name)

            if icon is not None:
                updates.append("icon = ?")
                params.append(icon)

            if tags is not None:
                updates.append("tags = ?")
                params.append(tags)

            if attributes is not None:
                updates.append("attrs = ?")
                params.append(json.dumps(attributes))

            params.append(uid)

            query = f"UPDATE locations SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            cursor.close()
        logger.info(f"Updated location with id: {uid}")

    def create_sorter(self, uid: str, location: str, name: str, icon: str, tags: str, attributes: dict):
        if location not in self.get_location_ids():
            raise SorterIdInvalidException(f"ID: {uid} not in locations, {self.get_location_ids()}")

        with self.sqlite_connection:
            cursor = self.sqlite_connection.cursor()
            cursor.execute("INSERT INTO sorters (id,location,name,icon,tags,attrs) VALUES(?,?,?,?,?,?)",
                           (uid, location, name, icon, tags, json.dumps(attributes)))
            cursor.close()
        logger.info(f"Created new sorter with id: {uid}")


if __name__ == "__main__":
    print("Interactive Part Sorter Database Management")
    sorter = PartSorter()
    time.sleep(0.1)  # no log messages after input

    while True:
        print("What would you like to do?")
        print("1) Create new location")
        print("2) Delete location")
        print("3) Get locations")
        print("4) Update location")
        print("5) Quit")
        print("Total changes made to database", sorter.total_changes)
        inp = input(">>> ")
        if not inp.isdigit():
            continue

        if int(inp) in [1, 2, 3, 4, 5]:
            if int(inp) == 1:
                id_inp = input("ID for location, type 'auto' for auto-generated uuid >>> ")
                if id_inp == "auto":
                    id_inp = str(uuid.uuid4())
                name_inp = input("Name for location >>> ")
                icon_inp = input("Icon for location >>> ")
                tags_inp = input("Comma-separated tags for location >>> ")

                attrs = {}
                while True:
                    key = input("Key for new attribute, type 'done' to quit inserting attrs >>> ")
                    if key == "done":
                        break
                    else:
                        value = input(f"Value for new '{key}' >>> ")
                    attrs[key] = value

                sorter.create_location(id_inp, name_inp, icon_inp, tags_inp, attrs)
            elif int(inp) == 2:
                id_inp = input("ID for location >>> ")
                certain = input("Are you sure (YES) >>> ") == "YES"
                if certain:
                    sorter.delete_location(id_inp)
            elif int(inp) == 3:
                pprint.pprint(sorter.get_locations())
            elif int(inp) == 4:
                id_inp = input("ID for location >>> ")
                name_inp = input("New name for location (leave empty to keep current) >>> ")
                icon_inp = input("New icon for location (leave empty to keep current) >>> ")
                tags_inp = input("New comma-separated tags for location (leave empty to keep current) >>> ")

                attrs = None
                update_attrs = input("Do you want to update attributes? (yes/no) >>> ").lower()
                if update_attrs == "yes":
                    attrs = {}
                    while True:
                        key = input("Key for new attribute, type 'done' to quit inserting attrs >>> ")
                        if key == "done":
                            break
                        else:
                            value = input(f"Value for new '{key}' >>> ")
                        attrs[key] = value

                sorter.update_location(id_inp, name_inp or None, icon_inp or None, tags_inp or None, attrs)
            elif int(inp) == 5:
                sorter.end()
                sys.exit()
            time.sleep(0.1)  # no log messages after input
    sorter.end()
