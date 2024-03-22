import sqlite3
import os
from uuid import uuid4

class DataBaseManager:
    def __init__(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()

    def init_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Noun(
            id CHAR(36) PRIMARY KEY,
            word_rus VARCHAR(255) NOT NULL,
            word_eng VARCHAR(255) NOT NULL,
            image VARCHAR(255)
            )
            ''')
        self.connection.commit()
        
    def insert(self, table_name, word_rus, word_eng, id=None, image_path=None):
        id = id or str(uuid4())
        image_path = image_path if image_path else "NULL"

        self.cursor.execute(
            f"INSERT INTO {table_name}(id, word_rus, word_eng, image) VALUES(?, ?, ?, ?)",
            (id, word_rus, word_eng, image_path),
        )
        self.connection.commit()
    
    def delete_table(self, table_name):
        self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    def delete_entity(self, table_name, id):
        self.cursor.execute(f"DELETE FROM {table_name} WHERE id=?", (id,))
        self.connection.commit()

        file_path = f"images/{id}.png"
        if os.path.isfile(file_path):
            os.remove(file_path)

    def get_ids_by_word(self, table_name, word):
        self.cursor.execute(
            f"SELECT id, word_rus, word_eng FROM {table_name} WHERE word_eng=? OR word_rus=?", (word, word)
        )
        return self.cursor.fetchall()
    
    def get_all_entities(self, table_name):
        self.cursor.execute(
            f'''
            SELECT * FROM {table_name}
            '''
        )
        return self.cursor.fetchall()
