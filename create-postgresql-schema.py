import pg8000.native

connection = pg8000.native.Connection("dinaraurazova")

sql_create_table = """
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    name TEXT, 
    description TEXT, 
    created_at TEXT, 
    updated_at TEXT)
"""

connection.run(sql_create_table)


connection.close()
