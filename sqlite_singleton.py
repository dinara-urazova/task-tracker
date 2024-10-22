import sqlite3


class SQLiteSingleton:
    _connection = None

    @classmethod
    def getConnection(cls):
        if cls._connection is None:
            cls._connection = sqlite3.connect("tasks.db")
        return cls._connection
