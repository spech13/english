from tkinter import ttk, Canvas

class Location:
    location_x = 0
    location_y = 0

    def set_location(self, location_x, location_y):
        self.location_x = location_x
        self.location_y = location_y

        self.place(
            x=location_x,
            y=location_y,
            width=self.width,
            height=self.height,
        )

class Padding:
    external_padding_x = 0
    external_padding_y = 0
    internal_padding_x = 0
    internal_padding_y = 0

    def set_padding(self, external, inner):
        self.external_padding_x = external[0]
        self.external_padding_y = external[1]
        self.internal_padding_x = inner[0]
        self.internal_padding_y = inner[1]

class Button(ttk.Button, Location, Padding):
    width = 200
    height = 50
    external_padding_x = 10
    external_padding_y = 5

class Entry(ttk.Entry, Location, Padding):
    width = 150
    height = 20
    external_padding_x = 10
    external_padding_y = 5

class Lable(ttk.Label, Location, Padding):
    external_padding_x = 10
    external_padding_y = 5

    def set_location(self, location_x, location_y):
        self.location_x = location_x
        self.location_y = location_y

        self.place(
            x=location_x,
            y=location_y,
        )

    @property
    def width(self):
        return self.winfo_width()
    
    @property
    def height(self):
        return self.winfo_height()
    
    def hidden(self):
        self.place_forget()
    
    def visible(self):
        self.place(x=self.location_x, y=self.location_y)

class CustomCanvas(Canvas, Location, Padding):
    width = 300
    height = 300
    external_padding_x = 10
    external_padding_y = 5