import sqlite3

from loguru import logger

Error = sqlite3.Error

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
        if self.total_changes == 0:
            logger.info("No changes have been made to the database")
        if self.sqlite_connection:
            self.sqlite_connection.close()
