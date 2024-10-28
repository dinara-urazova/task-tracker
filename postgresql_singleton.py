import pg8000.native


class PostgreSQLSingleton:
    _connection = None

    @classmethod
    def getConnection(cls):
        if cls._connection is None:
            cls._connection = pg8000.native.Connection("dinaraurazova")
        return cls._connection
