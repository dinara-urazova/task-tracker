import sqlite3
connection = sqlite3.connect("tasks.db") # создание БД (если к ней) + подключение к ней

cursor = connection.cursor() # enables traversal over the records in a database

sql_create_table = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, 
    description TEXT, 
    created_at TEXT, 
    updated_at TEXT)
"""

cursor.execute(sql_create_table)

connection.close()
