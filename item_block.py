class BaseItemBlock:
    item_width = 200
    item_heigth = 50
    padding = 1
    items = None

    def __init__(self, items, location=(0, 0)):
        self.location = location
        self.items = items
        self.set_position()

    def set_position(self):
        item_number = 0
        for item in self.items:
            item.place(
                width=self.item_width,
                height=self.item_heigth,
                x = self.location[0],
                y = self.location[1] + item_number * (self.item_heigth + self.padding)
            )
            item_number = item_number + 1

class ButtonBlock(BaseItemBlock):
    item_width = 200
    item_height = 50

class TextBlock(BaseItemBlock):
    item_width = 150
    item_heigth = 20

    button = None
    button_padding = 20
    button_width = 200
    button_height = 50

    def __init__(self, items, location=(0, 0), button=None):
        super().__init__(items, location)

        if button:
            button.place(
                width = self.button_width,
                height = self.button_height,
                x = self.location[0] - 25,
                y = self.location[1] + len(self.items) * (self.item_heigth + self.padding) + self.button_padding
            )
        self.button = button

    def set_lables(self, lables):
        lable_height = 20

        item_number = 0
        for item, lable in zip(self.items, lables):
            lable.place(
                x = self.location[0],
                y = self.location[1] + item_number * (lable_height + self.item_heigth + self.padding) 
            )
            item.place(
                x = self.location[0],
                y = self.location[1] + lable_height + item_number * (lable_height + self.item_heigth + self.padding)
            )
            item_number = item_number + 1

        if self.button:
            self.button.place(
                width = self.button_width,
                height = self.button_height,
                x = self.location[0] - 25,
                y = self.location[1] + len(self.items) * (self.item_heigth + self.padding + lable_height) + self.button_padding
            )
        self.button = self.button

class WordBlock:
    canvas = None
    lable = None
    text_box = None
    button = None

    canvas_size = (300, 300)
    lable_height = 20
    text_box_size = (150, 20)
    button_size = (200, 50)

    canvas_location = (100, 15)

    def __init__(self, lable, text_box, button, canvas=None):
        self.lable = lable
        self.canvas = canvas
        self.text_box = text_box
        self.button = button

        self.canvas.place(
            x = self.canvas_location[0],
            y = self.canvas_location[1],
            width = self.canvas_size[0],
            height = self.canvas_size[1]
        )

        self.lable.place(
            x = int((500 - self.lable.winfo_reqwidth()) / 2),
            y = self.canvas_location[1] + self.canvas_size[1],
        )

        self.text_box.place(
            x = int((500 - self.text_box_size[0]) / 2),
            y = self.canvas_location[1] + self.canvas_size[1] + self.lable_height + 20,
            width = self.text_box_size[0],
            height = self.text_box_size[1],
        )

        self.button.place(
            x = int((500 - self.button_size[0]) / 2),
            y = self.canvas_location[1] + self.canvas_size[1] + self.lable_height + self.text_box_size[1] + 40,
            width = self.button_size[0],
            height = self.button_size[1],
        )

class TextButtonBlock:
    items = None
    location = None

    padding_between_x = 10
    padding_between_y = 5

    button_width = 200
    button_height = 50
    text_box_width = 150
    text_box_heigth = 20

    def __init__(self, items, location=(0, 0)):
        for index, item in enumerate(items):
            text_box, button = item

            button.place(
                x = location[0] + self.text_box_width + self.padding_between_x,
                y = location[1] + index * (self.button_height + self.padding_between_y),
                width = self.button_width,
                height = self.button_height,
            )

            text_box.place(
                x = location[0],
                y = location[1] + index * (self.button_height + self.padding_between_y) + ((self.button_height - self.text_box_heigth) // 2),
                width = self.text_box_width,
                height = self.text_box_heigth,
            )
        
        self.items = items
        self.location = location

class LableBlock:
    items = None
    location = None
    lable_height = 20
    padding_y = 2

    def __init__(self, items, location=(0, 0)):
        for index, item in enumerate(items):
            item.place(
                x = location[0],
                y = location[1] + index * (self.lable_height + self.padding_y),
            )

