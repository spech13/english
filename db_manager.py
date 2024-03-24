import sqlite3
import os

class DBManager:
    def __init__(self, table_name):
        self.table_name = table_name
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            f'''
            CREATE TABLE IF NOT EXISTS {self.table_name}(
            id CHAR(36) PRIMARY KEY,
            word_rus VARCHAR(255) NOT NULL,
            word_eng VARCHAR(255) NOT NULL,
            image VARCHAR(255)
            )
            '''
        )
    
    def drop_table(self):
        self.cursor.execute(
            f"DROP TABLE IF EXISTS {self.table_name}"
        )
    
    def get_all(self):
        self.cursor.execute(
            f"SELECT * FROM {self.table_name}"
        )
        return self.cursor.fetchall()
    
    def get_by_word(self, word):
        self.cursor.execute(
            f"SELECT id, word_rus, word_eng FROM {self.table_name} "
            "WHERE word_eng=? OR word_rus=?", (word, word)
        )
        return self.cursor.fetchall()
    
    def get_pair(self, word_eng, word_rus):
        self.cursor.execute(
            f"SELECT word_rus, word_eng FROM {self.table_name}"
            "WHERE word_eng=? AND word_rus=?", (word_eng, word_rus)
        )
        return self.cursor.fetchall()
    
    def insert(self, id, word_rus, word_eng, image_path):
        image_path = image_path if image_path != "" else "NULL"

        self.cursor.execute(
            f"INSERT INTO {self.table_name}(id, word_rus, word_eng, image) VALUES(?, ?, ?, ?)",
            (id, word_rus, word_eng, image_path),
        )
        self.connection.commit()
    
    def delete(self, id):
        self.cursor.execute(
            f"DELETE FROM {self.table_name} WHERE id=?", (id,)
        )

        self.connection.commit()

        file_path = f"images/{id}.png"
        if os.path.isfile(file_path):
            os.remove(file_path)