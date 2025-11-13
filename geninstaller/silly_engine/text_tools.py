#! /usr/bin/env python3

"""
color parameters: style;background (30 is none);foreground
example:
c = Color
print(f"{c.info}This is an info message{c.end}")
"""


from .ascii_map_01 import abc_map_01 as abc_map



class Color:
    end = "\x1b[0m"
    cyan    =    info       = "\x1b[0;30;36m"
    red     =    danger     = "\x1b[0;30;31m"
    green   =    success    = "\x1b[0;30;32m"
    yellow  =    warning    = "\x1b[0;30;33m"
    blue = "\x1b[0;30;34m"
    violet = "\x1b[0;30;35m"

    fg_red = "\x1b[5;30;41m"
    fg_green = "\x1b[5;30;42m"
    fg_yellow = "\x1b[5;30;43m"
    fg_blue = "\x1b[5;30;44m"
    fg_cyan = "\x1b[5;30;46m"
    fg_violet = "\x1b[5;30;45m"
    fg_white = "\x1b[5;30;47m"

    bg_red = "\x1b[2;30;41m"
    bg_green = "\x1b[2;30;42m"
    bg_yellow = "\x1b[2;30;43m"
    bg_blue = "\x1b[2;30;44m"
    bg_cyan = "\x1b[2;30;46m"
    bg_violet = "\x1b[2;30;45m"
    bg_white = "\x1b[2;30;47m"

    def demo(self):
        """print all available colors"""
        no_display = ["end", "demo"]
        for attr in dir(self):
            if not attr.startswith("__") and attr not in no_display:
                print(f"{getattr(self, attr)}{attr}{self.end}")

c = Color()

class Title:
    def __init__(self, text="", abc_map=abc_map, color=None, step=0):
        self.height = len(abc_map["a"])
        self.text = text
        self.color = color is not None
        self.display = color or ""
        self.step = step

        self.build_display()

    def build_display(self):
        for row in range(self.height):
            display = ""
            for i in range(len(self.text)):
                letter = self.text[i] if self.text[i] in abc_map else " "
                if self.step > 0:
                    display = self.stepper(display, abc_map[letter][row], self.step)
                else:
                    display += abc_map[letter][row]
            self.display += display + "\n"
        if self.color:
            self.display += Color.end

    def stepper(self, display, letter_line, step):
        index = 1
        while index < len(display) and index <= step:
            if display[-1] == " ":
                display = display[:-1]
            else:
                letter_line = letter_line[1:]
            index += 1
        return display + letter_line

    def __str__(self):
        return self.display

def print_title(text="no title", abc_map=abc_map, color=None, step=0):
    print(Title(text, abc_map, color, step))
