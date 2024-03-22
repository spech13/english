from tkinter import Tk, ttk, Canvas, Text
from PIL import Image, ImageTk
from uuid import uuid4
from item_block import ButtonBlock, TextBlock, WordBlock, TextButtonBlock
from database_manager import DataBaseManager
import requests
import shutil
from random import randint
import sqlite3
import os

class DBManager:
    connection = None
    cursor = None

    def __init__(self, table_name):
        self.table_name = table_name
    
    def create_table(self):
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
    
    def connect(self):
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()
    
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
    
    def delete(self, id):
        self.cursor.execute(
            f"DELETE FROM {self.table_name} WHERE id=?", (id,)
        )

        self.connection.commit()

        file_path = f"images/{id}.png"
        if os.path.isfile(file_path):
            os.remove(file_path)

class View(DBManager):
    form_width = 500
    form_height = 500


class Location:
    location_x = 15
    location_y = 15

class Padding:
    padding_x = 10
    padding_y = 5

class Button(Location, Padding):
    button_width = 200
    button_height = 50

class Entry(Location, Padding):
    entry_width = 150
    entry_height = 20

class SearchResultView(View):
    def __init__(self, text=""):
        self.form = Tk()
        self.form.title("Search result")
        self.form.geometry(f"{self.form_width}x{self.form_height}")

        text_area = Text(
            self.form,
            width=self.form_width,
            height=self.form_height,
        )
        text_area.place(x=0, y=0)
        text_area.insert("1.0", text)

        self.form.mainloop()

class DeleteView(View, Button, Entry):
    def __init__(self, table_name):
        self.table_name = table_name

        self.form = Tk()
        self.form.title(f"Delete {table_name} entity")

        self.search_id_entry = ttk.Entry(self.form, name="search-id")
        self.delete_entity_entry = ttk.Entry(self.form, name="delete-id")

        self.search_id_button = ttk.Button(
            self.form,
            text="Search",
            command=self.search_word
        )
        self.delete_button = ttk.Button(
            self.form,
            text="Delete",
            command=self.delete_word,
        )

        items = [
            (self.search_id_entry, self.search_id_button),
            (self.delete_entity_entry, self.delete_button)
        ]

        for index, item in enumerate(items):
            entry, button = item

            entry.place(
                x=self.location_x,
                y=self.location_y + index * (self.button_height + self.padding_y) + ((self.button_height - self.entry_height) // 2),
                width=self.entry_width,
                height=self.entry_height, 
            )

            button.place(
                x = self.location_x + self.entry_width + self.padding_x,
                y = self.location_y + index * (self.button_height + self.padding_y),
                width=self.button_width,
                height=self.button_height,
            )

        self.connect()

        self.form_width = 2 * self.location_x + self.button_width + self.entry_width
        self.form_height = 2*self.location_y + len(items) * (self.button_height + self.padding_y)
                                                             
        self.form.geometry(f"{self.form_width}x{self.form_height}")
        self.form.resizable(False, False)

        self.form.mainloop()
    
    def search_word(self):
        words = self.get_by_word(
            self.form.children["search-id"].get()
        )

        SearchResultView("\n".join(
            [f"{word[0]} : {word[1]} : {word[2]}" for word in words]
            )
        )
    
    def delete_word(self):
        self.delete(
            self.form.children["delete-id"].get()
        )

class RepeatViewManager:
    pass

class AddViewManager:
    pass

class VerbViewManager:
    pass

class AdjectiveViewManager:
    pass

class NounViewManager:
    pass

class StudyViewManager:
    pass

class SettingsViewManager:
    pass

class HomeViewManager:
    pass

class ViewManager:
    active_form = None
    database_manager = DataBaseManager()

    def __init__(self):
        self.database_manager.init_tables()

    def home_form_view(self):
        self.active_form = Tk()
        self.active_form.title("Home")
        self.active_form.geometry('231x230')
        self.active_form.resizable(False, False)

        button_block_data = [
            {
                "name": "Noun",
                "handler": "noun_form_view"
            },
            {
                "name": "Adjective",
                "handler": "adjective_form_view"
            },
            {
                "name": "Verb",
                "handler": "verb_form_view"
            },
            {
                "name": "Settings",
                "handler": "settings_form_view" 
            }
        ]

        ButtonBlock(
            [
                ttk.Button(
                    self.active_form, text=button_data["name"],
                    command=getattr(self, button_data["handler"])
                )
                for button_data in button_block_data
            ],
            location=(15, 15)
        )

        self.active_form.mainloop()
    
    def form_view(self, title, button_block_data):
        self.active_form.destroy()

        self.active_form = Tk()
        self.active_form.title(title)
        self.active_form.geometry(
            f"230x{len(button_block_data) * ButtonBlock.item_height + 30}"
        )
        self.active_form.resizable(False, False)

        ButtonBlock(
            [
                ttk.Button(
                    self.active_form, text=button_data["name"],
                    command=getattr(self, button_data["handler"])
                )
                for button_data in button_block_data
            ],
            location=(15, 15)
        )

        self.active_form.mainloop()
    
    def add_form_view(self, title):
        self.active_form.destroy()

        self.active_form = Tk()
        self.active_form.title(title)
        self.active_form.geometry('231x215')
        self.active_form.resizable(False, False)

        text_block = TextBlock(
            [
                ttk.Entry(self.active_form, name="image"),
                ttk.Entry(self.active_form, name="word_eng"),
                ttk.Entry(self.active_form, name="word_rus")
            ],
            location=(40, 15),
            button=ttk.Button(self.active_form, text="Save", command=self.save_word)
            
        )
        text_block.set_lables(
            ttk.Label(self.active_form, text=name) for name in ["Image URL", "Word ENG", "Word RUS"] 
        )

        self.active_form.mainloop()
    
    def repeat_form_view(self, title, table_name, word_text, image_path="images/no-photo.jpg"):
        self.active_form.destroy()

        self.active_form = Tk()
        self.active_form.title(title)
        self.active_form.geometry("500x500")


        photo = ImageTk.PhotoImage(
            Image.open(image_path).resize((300,300,))
        )

        canvas = Canvas(self.active_form)
        canvas.create_image(0, 0, anchor='nw',image=photo)

        WordBlock(
            ttk.Label(self.active_form, text=word_text),
            ttk.Entry(self.active_form),
            ttk.Button(
                self.active_form,
                text="Answer",
                command=getattr(self, f"repeat_{table_name}_form_view")
            ),
            canvas=canvas,
        )

        self.active_form.mainloop()
    
    def settings_delete_form_view(self, title, text_button_block_data):
        self.active_form.destroy()

        self.active_form = Tk()
        self.active_form.title(title)
        self.active_form.geometry(
            f"390x{30 + len(text_button_block_data) * 55}"
        )

        TextButtonBlock(
            [
                (
                    ttk.Entry(self.active_form, name=text_button["text_box"]["name"]),
                    ttk.Button(
                        self.active_form,
                        text=text_button["button"]["name"],
                        command=getattr(self, text_button["button"]["handler"])
                    )
                )
                for text_button in text_button_block_data
            ],
            location=(15,15)
        )

        self.active_form.mainloop()
    
    def settings_show_form_view(self, title, lines):
        form = Tk()
        form.title(title)
        form.geometry(
            f"350x{30 + 20 * len(lines)}"
        )

        text_area = Text(form, width=350, height=30 + 20 * len(lines))
        text_area.place(x=0, y=0)
        text_area.insert("1.0", "\n".join(lines))

        self.active_form.mainloop()



    def noun_form_view(self):
        self.form_view(
            "Noun",
            [
                {
                    "name": "Add Nouns",
                    "handler": "add_nouns_form_view"
                },
                {
                    "name": "Repeat Nouns",
                    "handler": "repeat_noun_form_view"
                },
            ]
        )
    
    def adjective_form_view(self):
        self.form_view(
            "Adjective",
            [
                {
                    "name": "Add Adjective",
                    "handler": "add_adjective_form_view"
                },
                {
                    "name": "Repeat Nouns",
                    "handler": "repeat_adjective_form_view"
                },
            ]
        )

    def verb_form_view(self):
        self.form_view(
            "Verb",
            [
                {
                    "name": "Add Verb",
                    "handler": "add_verb_form_view"
                },
                {
                    "name": "Repeat Verb",
                    "handler": "repeat_verb_form_view"
                },
            ]
        )
    
    def settings_form_view(self):
        self.form_view(
            "Settings",
            [
                {
                    "name": "Noun",
                    "handler": "noun_settings_form_view"
                },
                {
                    "name": "Adjective",
                    "handler": "adjective_settings_form_view"
                },
                {
                    "name": "Verb",
                    "handler": "verb_settings_form_view"
                }
            ]
        )

    def add_nouns_form_view(self):
        self.add_form_view("Add Nouns")
    
    def add_adjective_form_view(self):
        self.add_form_view("Add Adjective")
    
    def add_verb_form_view(self):
        self.add_form_view("Add Verb")

    def repeat_noun_form_view(self):
        data = self.database_manager.get_all_entities("Noun")
        random_row = data[randint(0, len(data))-1]

        self.repeat_form_view(
            "Repeat nouns",
            "noun",
            random_row[2],
            image_path=random_row[3])

    def repeat_adjective_form_view(self):
        self.repeat_form_view("Repeat adjectives", "Programmer")

    def repeat_verb_form_view(self):
        self.repeat_form_view("Repeat verbs", "Programmer")
    
    def noun_settings_form_view(self):
        self.form_view(
            "Noun Settings",
            [
                {
                    "name":"Delete noun",
                    "handler": "delete_noun_view"
                }
            ]
        )

    def adjective_settings_form_view(self):
        pass

    def verb_settings_form_view(self):
        pass

    def delete_noun_view(self):
        self.settings_delete_form_view(
            "Delete noun by word-eng",
            [
                {
                    "text_box": {"name": "word"},
                    "button": {"name": "Show ids", "handler": "show_ids"},
                },
                {
                    "text_box": {"name": "id"},
                    "button": {"name": "Delete", "handler": "delete_noun"}
                },
            ],
        )
    
    def save_word(self):
        id = str(uuid4())
        image_path = None
        image_url = self.active_form.children["image"].get()

        if image_url != "":
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                image_path = f'images/{id}.png'
                with open(image_path, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)

        self.database_manager.insert(
            "Noun",
            self.active_form.children["word_rus"].get(),
            self.active_form.children["word_eng"].get(),
            id=id,
            image_path=image_path,
        )
    
    def show_ids(self):
        word = self.active_form.children["word"].get()

        data = self.database_manager.get_ids_by_word(
            "Noun", word
        )
        self.settings_show_form_view(
            "Show ids",
            [
                f"{entity[0]} : {entity[1]} : {entity[2]}"
                for entity in data
            ]
        )
    
    def delete_noun(self):
        self.database_manager.delete_entity(
            "Noun",
            self.active_form.children["id"].get()
        )

DeleteView("Noun")
