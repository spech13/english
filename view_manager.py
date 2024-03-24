from custom import Lable, Button, CustomCanvas, Location, Padding, Entry
from db_manager import DBManager
from PIL import Image, ImageTk
from tkinter import Tk, Text
from random import randint
from uuid import uuid4
import requests
import shutil
import os

DEFAULT_IMAGE_PATH = "images/no-photo.png"

class View(DBManager, Location, Padding):
    width = 500
    height = 500
    internal_padding_x = 15
    internal_padding_y = 15

    form = None
    items = None
    
    def __init__(self, table_name):
        super().__init__(table_name)

        self.form = Tk()
        self.form.geometry(f"{self.width}x{self.height}")
        self.form.resizable(False, False)
    
    def refresh_view(self):
        for item in self.form.children.values():
            item.place(x=self.location_x, y=self.location_y)
        
        self.form.update()

class SearchResultView(View):
    def __init__(self, table_name, text=""):
        super().__init__(table_name)

        self.form.title("Search result")

        text_area = Text(
            self.form,
            width=self.width,
            height=self.height,
        )
        text_area.place(x=0, y=0)
        text_area.insert("1.0", text)

        self.form.mainloop()

class DeleteView(View):
    def __init__(self, table_name):
        super().__init__(table_name)
        self.form.title(f"Delete {table_name} entity")

        search_id_entry = Entry(self.form, name="search-id")
        search_id_button = Button(
            self.form,
            text="Search",
            command=self.search_word
        )

        delete_entity_entry = Entry(self.form, name="delete-id")
        delete_button = Button(
            self.form,
            text="Delete",
            command=self.delete_word,
        )

        items = [
            (search_id_entry, search_id_button),
            (delete_entity_entry, delete_button)
        ]

        for index, item in enumerate(items):
            entry, button = item

            entry.set_location(
                self.internal_padding_x,
                (self.internal_padding_y +
                 index * (button.height + button.external_padding_y) +
                 ((button.height - entry.height)) // 2
                )
            )

            button.set_location(
                self.internal_padding_x + entry.width + entry.external_padding_x,
                self.internal_padding_y + index * (button.height + button.external_padding_y)
            )

        self.width = 2 * self.internal_padding_x + search_id_entry.width + search_id_button.width
        self.height = 2 * self.internal_padding_y + len(items) * (search_id_button.height + search_id_button.external_padding_y)
                                                             
        self.form.geometry(f"{self.width}x{self.height}")

        self.form.mainloop()

    def search_word(self):
        words = self.get_by_word(
            self.form.children["search-id"].get()
        )

        SearchResultView(self.table_name, "\n".join(
            [f"{word[0]} : {word[1]} : {word[2]}" for word in words]
            )
        )
    
    def delete_word(self):
        self.delete(
            self.form.children["delete-id"].get()
        )

class RepeatView(View):
    def __init__(self, table_name, word, image_path):
        super().__init__(table_name)
        self.form.title(f"Repeat {table_name}")

        canvas = CustomCanvas(self.form, name="image")

        if not os.path.exists(image_path):
            image_path = DEFAULT_IMAGE_PATH

        photo = ImageTk.PhotoImage(
            Image.open(image_path).resize(
                (canvas.width, canvas.height)
            )
        )

        canvas.create_image(0, 0, anchor="nw", image=photo)

        word = Lable(self.form, text=word, name="word")
        failure = Lable(self.form, text="Failure!", name="failure", foreground="red") 
        translation = Entry(self.form, name="translation")
        answer = Button(self.form, text="Answer", command=self.repeat)
        self.refresh_view()
        
        canvas.set_location(self.internal_padding_x, self.internal_padding_y)

        word.set_location(
            self.internal_padding_x + ((canvas.width - word.width) // 2),
            canvas.location_y + canvas.height + canvas.external_padding_y
        )

        failure.set_location(
            self.internal_padding_x + ((canvas.width - failure.width) // 2),
            word.location_y + word.height + word.external_padding_y,
        )

        translation.set_location(
            self.internal_padding_x + ((canvas.width - translation.width) // 2),
            failure.location_y + failure.height + failure.external_padding_y
        )
        failure.hidden()

        answer.set_location(
            self.internal_padding_x + ((canvas.width - answer.width) // 2),
            translation.location_y + translation.height + translation.external_padding_y
        )

        self.width = 2 * self.internal_padding_x + canvas.width
        self.height = 2 * self.internal_padding_y + answer.location_y + answer.height


        self.form.geometry(f"{self.width}x{self.height}")

        self.form.mainloop()

    def repeat(self):
        translation = self.form.children["translation"].get().lower()
        words = self.get_by_word(translation)

        failure = self.form.children["failure"]

        if translation not in [word[1].lower() for word in words]:
            failure.visible()
            return
        
        self.form.destroy()
        words = self.get_all()
        random_row = randint(0, len(words)-1)
        RepeatView(self.table_name, words[random_row][2], f"images/{words[random_row][0]}.png")

class AddView(View):
    def __init__(self, table_name):
        super().__init__(table_name)
        self.form.title(f"Add {table_name}")

        failure = Lable(self.form, text="RUS and ENG must not be empty", name="failure", foreground="red")

        image_url_lable = Lable(self.form, text="Image URL:")
        image_url_entry = Entry(self.form, name="image-url")

        word_eng_lable = Lable(self.form, text="ENG:")
        word_eng_entry = Entry(self.form, name="word-eng")

        word_rus_lable = Lable(self.form, text="RUS:")
        word_rus_entry = Entry(self.form, name="word-rus")
        add_button = Button(self.form, text="Add", command=self.add)
        self.refresh_view()

        failure.set_location(
            self.internal_padding_x,
            self.internal_padding_y,
        )
        failure.hidden()

        image_url_lable.set_location(
            self.internal_padding_x,
            failure.location_x + failure.height + failure.external_padding_y,
        )

        image_url_entry.set_location(
            self.internal_padding_x + ((add_button.width - word_eng_entry.width) // 2),
            image_url_lable.location_y + image_url_lable.height + image_url_lable.external_padding_y,
        )

        word_eng_lable.set_location(
            self.internal_padding_x,
            image_url_entry.location_y + image_url_entry.height + image_url_entry.external_padding_y,
        )

        word_eng_entry.set_location(
            self.internal_padding_x + ((add_button.width - word_eng_entry.width) // 2),
            word_eng_lable.location_y + word_eng_lable.height + word_eng_lable.external_padding_y,
        )

        word_rus_lable.set_location(
            self.internal_padding_x,
            word_eng_entry.location_y + word_eng_entry.height + word_eng_entry.external_padding_y,
        )

        word_rus_entry.set_location(
            self.internal_padding_x + ((add_button.width - word_eng_entry.width) // 2),
            word_rus_lable.location_y + word_rus_lable.height + word_rus_lable.external_padding_y,
        )

        add_button.set_location(
            self.internal_padding_x,
            word_rus_entry.location_y + word_rus_entry.height + word_rus_entry.external_padding_y
        )

        self.width = 2 * self.internal_padding_x + add_button.width
        self.height = 2 * self.internal_padding_y + add_button.location_y + add_button.height

        self.form.geometry(f"{self.width}x{self.height}")

        self.form.mainloop()
    
    def validate(self):
        validate = True

        if self.form.children["word-rus"].get() == "":
            validate = False

        if self.form.children["word-eng"].get() == "":
            validate = False
        
        if not validate:
            self.form.children["failure"].visible()

        return validate   
    
    def add(self):
        if not self.validate():
            return
        
        self.form.children["failure"].hidden()

        id = str(uuid4())
        image_url = self.form.children["image-url"].get()
        image_path = DEFAULT_IMAGE_PATH

        if image_url != "":
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                image_path = f'images/{id}.png'
                with open(image_path, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)

        self.insert(
            id,
            self.form.children["word-rus"].get(),
            self.form.children["word-eng"].get(),
            image_path,
        )

class StudyView(View):
    def __init__(self, table_name):
        super().__init__(table_name)
        self.form.title(f"Study {table_name}")

        add_button = Button(self.form, text=f"Add {table_name}", command=self.add)
        repeat_button = Button(self.form, text=f"Repeat {table_name}", command=self.repeat)
        settings_button = Button(self.form, text=f"Settings {table_name}", command=self.settings)

        add_button.set_location(
            self.internal_padding_x,
            self.internal_padding_y,
        )

        repeat_button.set_location(
            self.internal_padding_x,
            add_button.location_y + add_button.height + add_button.external_padding_y,
        )

        settings_button.set_location(
            self.internal_padding_x,
            repeat_button.location_y + repeat_button.height + repeat_button.external_padding_y,
        )

        self.width = 2 * self.internal_padding_x + settings_button.width
        self.height = 2 * self.internal_padding_y + settings_button.location_y + settings_button.height

        self.form.geometry(f"{self.width}x{self.height}")

        self.form.mainloop()
    
    def add(self):
        self.form.destroy()
        AddView(self.table_name)
    
    def repeat(self):
        self.form.destroy()
        words = self.get_all()
        random_row = randint(0, len(words)-1)
        RepeatView(self.table_name, words[random_row][2], f"images/{words[random_row][0]}.png")
    
    def settings(self):
        self.form.destroy()
        SettingsView(self.table_name)

class SettingsView(View):
    def __init__(self, table_name):
        super().__init__(table_name)
        self.form.title(f"Settings {table_name}")

        delete_button = Button(self.form, text=f"Delete {table_name}", command=self.delete)
        delete_button.set_location(
            self.internal_padding_x,
            self.internal_padding_y,
        )

        self.width = 2 * self.internal_padding_x + delete_button.width
        self.height = 2 * self.internal_padding_y + delete_button.location_y + delete_button.height

        self.form.geometry(f"{self.width}x{self.height}")

        self.form.mainloop()
    
    def delete(self):
        self.form.destroy()
        DeleteView(self.table_name)

class HomeView(View):
    def __init__(self):
        self.form = Tk()
        self.form.resizable(False, False)
        self.form.title("Home")

        noun_button = Button(self.form, text="Noun", command=self.noun)
        adjective_button = Button(self.form, text="Adjective", command=self.adjective)
        verb_button = Button(self.form, text="Verb", command=self.verb)

        noun_button.set_location(
            self.internal_padding_x,
            self.internal_padding_y,
        )

        adjective_button.set_location(
            self.internal_padding_x,
            noun_button.location_y + noun_button.height + noun_button.external_padding_y,
        )

        verb_button.set_location(
            self.internal_padding_y,
            adjective_button.location_y + adjective_button.height + adjective_button.external_padding_y,
        )

        self.width = 2 * self.internal_padding_x + verb_button.width
        self.height = 2 * self.internal_padding_y + verb_button.location_y + verb_button.height

        self.form.geometry(f"{self.width}x{self.height}")

        self.form.mainloop()
    
    def noun(self):
        self.form.destroy()
        StudyView("Noun")
    
    def adjective(self):
        self.form.destroy()
        StudyView("Adjective")
    
    def verb(self):
        self.form.destroy()
        StudyView("Verb")

HomeView()


