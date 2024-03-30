from custom import Lable, Button, CustomCanvas, Location, Padding, Entry
from requests import RequestException
from screeninfo import get_monitors
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
            item.place(x=item.location_x, y=item.location_y)
        
        self.form.update()
    
    def place_by_center(self):
        monitor = get_monitors()[0]
        self.location_x = (monitor.width // 2) - (self.width // 2)
        self.location_y = (monitor.height // 2) - (self.height // 2)

        self.form.geometry(f"{self.width}x{self.height}+{self.location_x}+{self.location_y}")
    
    def comeback_handler(self, event=None):
        self.form.destroy()
        HomeView()


class SearchView(View):
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
        search_id_button = Button(self.form, text="Search", command=self.search_handler)
        delete_entity_entry = Entry(self.form, name="delete-id")
        delete_button = Button(self.form, text="Delete", command=self.delete_handler)
        comeback_button = Button(self.form, text="Comeback", command=self.comeback_handler)

        search_id_entry.focus_force()
        search_id_button.bind('<Return>', self.search_handler)
        delete_button.bind('<Return>', self.delete_handler)
        comeback_button.bind('<Return>', self.comeback_handler)

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
        
        comeback_button.set_location(
            self.internal_padding_x + ((delete_entity_entry.width + delete_button.width - comeback_button.width) // 2),
            delete_button.location_y + delete_button.height + delete_button.external_padding_y,
        )

        self.width = 2 * self.internal_padding_x + search_id_entry.width + search_id_button.width
        self.height = comeback_button.location_y + comeback_button.height + self.internal_padding_y
                                                             
        self.place_by_center()
        self.form.mainloop()

    def search_handler(self, event=None):
        words = self.get_by_word(
            self.form.children["search-id"].get()
        )

        SearchView(self.table_name, "\n".join(
            [f"{word[0]} : {word[1]} : {word[2]}" for word in words]
            )
        )
    
    def delete_handler(self, event=None):
        self.delete(
            self.form.children["delete-id"].get()
        )

class SearchUpdateView(View):
    def __init__(self, table_name):
        super().__init__(table_name)
        self.form.title(f"Search update {table_name}")

        search_id_entry = Entry(self.form, name="search-id")
        search_id_button = Button(self.form, text="Search", command=self.search_handler)
        update_id_entry = Entry(self.form, name="update-id")
        update_id_button = Button(self.form, text="Update", command=self.update_handler)
        comeback_button = Button(self.form, text="Comeback", command=self.comeback_handler)

        search_id_entry.focus_force()
        search_id_button.bind('<Return>', self.search_handler)
        update_id_button.bind('<Return>', self.update_handler)
        comeback_button.bind('<Return>', self.comeback_handler)

        items = ((search_id_entry, search_id_button), (update_id_entry, update_id_button))

        for index, item in enumerate(items):
            entry, button = item

            entry.set_location(
                self.internal_padding_x,
                self.internal_padding_y + index * (button.height + button.external_padding_y) + ((button.height - entry.height) // 2),
            )

            button.set_location(
                self.internal_padding_x + entry.width + entry.external_padding_x,
                self.internal_padding_y + index * (button.height + button.external_padding_y),
            )
        
        comeback_button.set_location(
            self.internal_padding_x + ((update_id_entry.width + update_id_button.width - comeback_button.width) // 2),
            update_id_button.location_y + update_id_button.height + update_id_button.external_padding_y,
        )
        
        self.width = 2 * (self.internal_padding_x + update_id_button.external_padding_x) + update_id_entry.width + update_id_button.width
        self.height = comeback_button.location_y + comeback_button.height + self.internal_padding_y

        self.place_by_center()
        self.form.mainloop()
    
    def search_handler(self, event=None):
        words = self.get_by_word(
            self.form.children["search-id"].get()
        )

        SearchView(self.table_name, "\n".join(
            [f"{word[0]} : {word[1]} : {word[2]}" for word in words]
            )
        )

    def update_handler(self, event=None):
        UpdateView(self.table_name, self.form.children["update-id"].get())

class UpdateView(View):
    id = None
    image_path = None

    def __init__(self, table_name, id):
        super().__init__(table_name)
        self.form.title(f"Update {table_name}")

        status_lable = Lable(self.form, text="Success!", name="status", foreground="green")
        image_url_lable = Lable(self.form, text="Image URL:")
        word_eng_lable = Lable(self.form, text="ENG:")
        word_rus_lable = Lable(self.form, text="RUS:")

        image_url_entry = Entry(self.form, name="image-url")
        word_eng_entry = Entry(self.form, name="word-eng")
        word_rus_entry = Entry(self.form, name="word-rus")

        update_button = Button(self.form, text="Update", command=self.update_hadler)

        update_button.bind('<Return>', self.update_hadler)

        word_rus, word_eng, image_path = self.get_by_id(id)[0]

        self.id = id
        self.image_path = image_path
        word_eng_entry.insert("1", word_eng)
        word_rus_entry.insert("1", word_rus)

        self.refresh_view()

        status_lable.set_location(
            self.internal_padding_x + ((update_button.width - status_lable.width) // 2),
            self.internal_padding_y,
        )
        status_lable.hidden()

        items = ((image_url_lable, image_url_entry), (word_eng_lable, word_eng_entry), (word_rus_lable, word_rus_entry))

        for index, item in enumerate(items):
            lable, entry = item

            lable.set_location(
                self.internal_padding_x,
                self.internal_padding_y + status_lable.location_y + status_lable.location_y + index * (lable.height + entry.height + lable.external_padding_y + entry.external_padding_y)
            )

            entry.set_location(
                self.internal_padding_x + ((update_button.width - entry.width) // 2),
                lable.location_y + lable.height + lable.external_padding_y
            )
        
        update_button.set_location(
            self.internal_padding_x,
            self.internal_padding_y + word_rus_entry.location_y + word_rus_entry.height + word_rus_entry.external_padding_y,
        )

        self.width = 2 * self.internal_padding_x + update_button.width
        self.height = update_button.location_y + update_button.height + self.internal_padding_y

        self.place_by_center()
        self.form.mainloop()
    
    def update_hadler(self, event=None):
        status = self.form.children["status"]
        image_url = self.form.children["image-url"].get()
        image_path = ""

        if image_url != "":
            try:
                response = requests.get(image_url, stream=True)
            except RequestException:
                status.configure(text="Error when download image!", foreground="red")
                self.refresh_view()
                status.set_location(
                    self.internal_padding_x,
                    self.internal_padding_y,
                )
                status.visible()
                return

            if response.status_code == 200:
                if self.image_path and os.path.exists(self.image_path):
                    os.remove(self.image_path)
                     
                image_path = f'images/{self.id}.png'
                with open(image_path, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
            else:
                status.configure(text="Error when download image!", foreground="red")
                self.refresh_view()
                status.set_location(
                    self.internal_padding_x,
                    self.internal_padding_y,
                )
                status.visible()
                return

        self.update(
            self.id,
            self.form.children["word-rus"].get(),
            self.form.children["word-eng"].get(),
            image_path,
        )
        status.visible()



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

        word_lable = Lable(self.form, text=word, name="word")
        status_lable = Lable(self.form, text="Failure!", name="status", foreground="red") 
        translation_entry = Entry(self.form, name="translation")
        answer_button = Button(self.form, text="Answer", command=self.repeat_handler)
        comeback_button = Button(self.form, text="Comeback", command=self.comeback_handler)

        translation_entry.focus_force()
        answer_button.bind('<Return>', self.repeat_handler)
        comeback_button.bind('<Return>', self.comeback_handler)

        self.refresh_view()
        
        canvas.set_location(self.internal_padding_x, self.internal_padding_y)

        word_lable.set_location(
            self.internal_padding_x + ((canvas.width - word_lable.width) // 2),
            canvas.location_y + canvas.height + canvas.external_padding_y
        )

        status_lable.set_location(
            self.internal_padding_x + ((canvas.width - status_lable.width) // 2),
            word_lable.location_y + word_lable.height + word_lable.external_padding_y,
        )

        translation_entry.set_location(
            self.internal_padding_x + ((canvas.width - translation_entry.width) // 2),
            status_lable.location_y + status_lable.height + status_lable.external_padding_y
        )
        status_lable.hidden()

        answer_button.set_location(
            self.internal_padding_x + ((canvas.width - answer_button.width) // 2),
            translation_entry.location_y + translation_entry.height + translation_entry.external_padding_y
        )

        comeback_button.set_location(
            self.internal_padding_x + ((canvas.width - comeback_button.width) // 2),
            answer_button.location_y + answer_button.height + answer_button.external_padding_y,
        )

        self.width = 2 * self.internal_padding_x + canvas.width
        self.height = comeback_button.location_y + comeback_button.height + self.internal_padding_y

        self.place_by_center()
        self.form.mainloop()

    def repeat_handler(self, event=None):
        translation = self.form.children["translation"].get().lower()
        words = self.get_by_word(translation)

        status = self.form.children["status"]

        if translation not in [word[2].lower() for word in words]:
            status.visible()
            return
        
        self.form.destroy()
        words = self.get_all()
        random_row = randint(0, len(words)-1)
        RepeatView(self.table_name, words[random_row][1], f"images/{words[random_row][0]}.png")

class AddView(View):
    def __init__(self, table_name):
        super().__init__(table_name)
        self.form.title(f"Add {table_name}")

        status = Lable(self.form, text="RUS and ENG must not be empty", name="status", foreground="red")

        image_url_lable = Lable(self.form, text="Image URL:")
        image_url_entry = Entry(self.form, name="image-url")

        word_eng_lable = Lable(self.form, text="ENG:")
        word_eng_entry = Entry(self.form, name="word-eng")

        word_rus_lable = Lable(self.form, text="RUS:")
        word_rus_entry = Entry(self.form, name="word-rus")
        add_button = Button(self.form, text="Add", command=self.add_handler, name="add-button")
        comeback_button = Button(self.form, text="Comeback", command=self.comeback_handler)

        add_button.bind('<Return>', self.add_handler)
        comeback_button.bind('<Return>', self.comeback_handler)

        self.refresh_view()

        status.set_location(
            self.internal_padding_x,
            self.internal_padding_y,
        )
        status.hidden()

        image_url_lable.set_location(
            self.internal_padding_x,
            status.location_x + status.height + status.external_padding_y,
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

        comeback_button.set_location(
            self.internal_padding_x,
            add_button.location_y + add_button.height + add_button.external_padding_y,
        )

        self.width = 2 * self.internal_padding_x + add_button.width
        self.height = comeback_button.location_y + comeback_button.height + self.internal_padding_y

        self.place_by_center()
        self.form.mainloop()
    
    def validate(self):
        validate = True

        if self.form.children["word-rus"].get() == "":
            validate = False

        if self.form.children["word-eng"].get() == "":
            validate = False
        
        if not validate:
            self.form.children["status"].visible()

        return validate   
    
    def add_handler(self, event=None):
        if not self.validate():
            return
        
        status = self.form.children["status"]
        status.hidden()

        id = str(uuid4())
        image_url = self.form.children["image-url"].get()
        image_path = DEFAULT_IMAGE_PATH

        if image_url != "":
            try:
                response = requests.get(image_url, stream=True)
            except RequestException:
                status.configure(text="Error when download image!")
                status.visible()
                return

            if response.status_code == 200:
                image_path = f'images/{id}.png'
                with open(image_path, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
            else:
                status.configure(text="Error when download image!")
                status.visible()
                return

        self.insert(
            id,
            self.form.children["word-rus"].get(),
            self.form.children["word-eng"].get(),
            image_path,
        )

        status.configure(text="Success!", foreground="green")
        self.refresh_view()

        status.set_location(
            self.internal_padding_x + ((self.form.children["add-button"].width - status.width) // 2),
            self.internal_padding_y,
        )
        status.visible()
        print(self.form.children["add-button"].width)
        print(status.width)
        

class StudyView(View):
    def __init__(self, table_name):
        super().__init__(table_name)
        self.form.title(f"Study {table_name}")

        add_button = Button(self.form, text=f"Add {table_name}", command=self.add_handler)

        data = self.get_all()

        repeat_button = Button(
            self.form,
            text=f"Repeat {table_name}",
            command=self.repeat_handler,
            state="enabled" if data else "disabled"
        )
        settings_button = Button(
            self.form,
            text=f"Settings {table_name}",
            command=self.settings_handler,
            state="enabled" if data else "disabled"
        )

        add_button.focus_force()
        add_button.bind('<Return>', self.add_handler)
        repeat_button.bind('<Return>', self.repeat_handler)
        settings_button.bind('<Return>', self.settings_handler)

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
        self.height = settings_button.location_y + settings_button.height + self.internal_padding_y

        self.place_by_center()
        self.form.mainloop()
    
    def add_handler(self, event=None):
        self.form.destroy()
        AddView(self.table_name)
    
    def repeat_handler(self, event=None):
        self.form.destroy()
        words = self.get_all()
        random_row = randint(0, len(words)-1)
        RepeatView(self.table_name, words[random_row][1], f"images/{words[random_row][0]}.png")
    
    def settings_handler(self, event=None):
        self.form.destroy()
        SettingsView(self.table_name)

class SettingsView(View):
    def __init__(self, table_name):
        super().__init__(table_name)
        self.form.title(f"Settings {table_name}")

        delete_button = Button(self.form, text=f"Delete {table_name}", command=self.delete_handler)
        delete_button.set_location(
            self.internal_padding_x,
            self.internal_padding_y,
        )

        update_button = Button(self.form, text=f"Update {table_name}", command=self.update_handler)
        update_button.set_location(
            self.internal_padding_x,
            delete_button.location_y + delete_button.external_padding_y + update_button.height,
        )

        delete_button.bind('<Return>', self.delete_handler)
        update_button.bind('<Return>', self.update_handler)

        self.width = 2 * self.internal_padding_x + update_button.width
        self.height = update_button.location_y + update_button.height + self.internal_padding_y

        self.place_by_center()
        self.form.mainloop()
    
    def delete_handler(self, event=None):
        self.form.destroy()
        DeleteView(self.table_name)
    
    def update_handler(self, event=None):
        self.form.destroy()
        SearchUpdateView(self.table_name)

class HomeView(View):
    def __init__(self):
        self.form = Tk()
        self.form.resizable(False, False)
        self.form.title("Home")

        noun_button = Button(self.form, text="Noun", command=self.noun_handler)
        adjective_button = Button(self.form, text="Adjective", command=self.adjective_handler)
        verb_button = Button(self.form, text="Verb", command=self.verb_handler)

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

        noun_button.focus_force()
        noun_button.bind('<Return>', self.noun_handler)
        adjective_button.bind('<Return>', self.adjective_handler)
        verb_button.bind('<Return>', self.verb_handler)

        self.width = 2 * self.internal_padding_x + verb_button.width
        self.height = verb_button.location_y + verb_button.height + self.internal_padding_y

        self.place_by_center()
        self.form.mainloop()
    
    def noun_handler(self, event=None):
        self.form.destroy()
        StudyView("Noun")
    
    def adjective_handler(self, event=None):
        self.form.destroy()
        StudyView("Adjective")
    
    def verb_handler(self, event=None):
        self.form.destroy()
        StudyView("Verb")

HomeView()


