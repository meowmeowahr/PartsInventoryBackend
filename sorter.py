import db
import json
from loguru import logger


class SorterIdInvalidException(BaseException):
    pass


class PartSorter(db.BaseDatabase):
    def create_tables(self):
        with self.sqlite_connection:
            self.sqlite_connection.execute("""CREATE TABLE IF NOT EXISTS locations (
                                                                    id TEXT PRIMARY KEY UNIQUE, 
                                                                    name TEXT NOT NULL, 
                                                                    icon TEXT NOT NULL, 
                                                                    tags TEXT,
                                                                    attrs TEXT NOT NULL
                                                                    )""")
            self.sqlite_connection.execute("""CREATE TABLE IF NOT EXISTS sorters (
                                                                    id TEXT PRIMARY KEY UNIQUE,
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
        except db.Error as e:
            logger.error(f"Experienced error getting locations, returning empty list: {repr(e)}")
            return []

    def get_location_ids(self) -> list:
        try:
            cursor = self.sqlite_connection.cursor()
            cursor.execute("SELECT id FROM locations")
            rows = cursor.fetchall()
            rows = [row[0] for row in rows]

            return rows
        except db.Error as e:
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
            raise SorterIdInvalidException(f"Location ID: {location} not in locations, {self.get_location_ids()}")

        if uid in self.get_sorter_ids():
            raise SorterIdInvalidException(f"Sorter ID: {uid} already in {self.get_sorter_ids()}")

        with self.sqlite_connection:
            cursor = self.sqlite_connection.cursor()
            cursor.execute("INSERT INTO sorters (id,location,name,icon,tags,attrs) VALUES(?,?,?,?,?,?)",
                           (uid, location, name, icon, tags, json.dumps(attributes)))
            cursor.close()
        logger.info(f"Created new sorter with id: {uid}")

    def delete_sorter(self, uid: str):
        if uid not in self.get_sorter_ids():
            raise SorterIdInvalidException(f"Sorter with id: {uid} does not exist")
        with self.sqlite_connection:
            cursor = self.sqlite_connection.cursor()
            cursor.execute("DELETE FROM sorters WHERE id=?",
                           (uid,))

    def get_sorters(self) -> list:
        try:
            cursor = self.sqlite_connection.cursor()
            cursor.execute("SELECT * FROM sorters")
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            rows = [dict(zip(columns, row)) for row in rows]
            for row in rows:
                if 'attrs' in row and isinstance(row['attrs'], str):
                    row['attrs'] = json.loads(row['attrs'])

            return rows
        except db.Error as e:
            logger.error(f"Experienced error getting sorters, returning empty list: {repr(e)}")
            return []

    def get_sorter_ids(self) -> list:
        try:
            cursor = self.sqlite_connection.cursor()
            cursor.execute("SELECT id FROM sorters")
            rows = cursor.fetchall()
            rows = [row[0] for row in rows]

            return rows
        except db.Error as e:
            logger.error(f"Experienced error getting sorters, returning empty list: {repr(e)}")
            return []

    def update_sorter(self,
                      uid: str,
                      location: str = None,
                      name: str = None,
                      icon: str = None,
                      tags: str = None,
                      attributes: dict = None
                      ):
        with self.sqlite_connection:
            cursor = self.sqlite_connection.cursor()
            updates = []
            params = []

            if location is not None:
                updates.append("location = ?")
                params.append(location)

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

            query = f"UPDATE sorters SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            cursor.close()
        logger.info(f"Updated sorter with id: {uid}")
