import sqlite3
import os

db_path = 'flsite.db'
if os.path.exists(db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute('DELETE FROM quiz;')
    connection.commit()

    cursor.close()
    connection.close()