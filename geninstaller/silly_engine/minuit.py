import os
from typing import Callable


PROMPT = " > "
WIDTH = 100


def clear():
    """clears the console"""
    os.system('cls' if os.name == 'nt' else 'clear')


class TextField:
    def __init__(self, text='', width=WIDTH, color=None):
        self.text = text
        self.width = width
        self.display = ""
        self.words = text.split(" ")
        self.build_display()
        if color:
            self.display = f"{color}{self.display}\x1b[0m"

    def build_display(self):
        line = ""
        for word in self.words:
            if len(line) + len(word) > self.width:
                self.display += line + "\n"
                line = ""
            line += word + " "
        self.display += line + "\n"

    def __str__(self):
        return self.display

def print_formated(text='', width=WIDTH, color=None):
    print(TextField(text, width, color))


class FieldError(Exception):
    def __init__(self, message: str="Field Error", status="Internal", *args, **kwargs):
        self.status = status
        self.message = message
        super().__init__({'status': self.status, 'message': self.message})


class FormError(FieldError):
    def __init__(self, message: str="Form Error", status="Internal", *args, **kwargs):
        super().__init__(message, status, *args, **kwargs)


class Confirmation:
    def __init__(self, message="Are you sure ?", yes="y", no="n", default=True, prompt=None, recap=False):
        self.message = message
        self.yes_no_message = f"({yes}/{no})"
        self.yes = yes
        self.no = no
        self.recap = recap
        self.default = default
        self.prompt = prompt
        self.validator = lambda x: x.strip().lower() in [yes, no, ""]
        if default not in [True, False, None]:
            raise FieldError(f"default must be a boolean value or None, received '{default}'", "Internal")
        if default == True:
            self.yes_no_message = f"({yes.upper()}/{no})"
        if default == False:
            self.yes_no_message = f"({yes}/{no.upper()})"


    def ask(self, prompt=None):
        value = input(f"{self.message}{self.yes_no_message}{prompt or self.prompt or PROMPT}")
        if self.validator:
            if not self.validator(value):
                return self.ask()
        resolve = {self.yes: True, self.no: False}
        if value.strip() == "":
            if self.default is None:
                return self.ask()
            return self.default
        else:
            return resolve[value.strip().lower()]



class Field:
    def __init__(self, name=None, text=None, typing=None, validator=None, error_message=None,required=False, prompt=None, default=None):
        if name is None:
            raise FieldError("Field name is required")
        self.name = name
        self.text = text or name
        self.typing = typing
        self.validator = validator
        self.error_message = error_message
        self.required = required
        self.prompt = prompt
        self._default = default

    def ask(self, question=None, error_message=None, prompt=None):
        question = question or self.text
        error_message = self.error_message or error_message
        self.default_message = f"({self._default})" if self._default is not None else ""
        value = input(f"{question}{'*' if self.required else ''}{self.default_message}{prompt or self.prompt or PROMPT}").strip()
        value = value if value != "" else None
        if self.typing is not None and value is not None:
            try:
                if self.typing == bool:
                    value = bool(int(value))
                else:
                    value = self.typing(value)
            except Exception:
                print(error_message or "")
                return self.ask(question, error_message, prompt)
        if self.required:
            if value is None:
                if self.required and self._default is not None:
                    value = self._default
                else:
                    print(error_message)
                    return self.ask(question, error_message, prompt)
        if self.validator and value is not None:
            if not self.validation(value):
                print(error_message or "")
                return self.ask(question, error_message, prompt)
        return value

    def validation(self, value):
        try:
            validation = self.validator(value)
        except Exception:
            validation = False
        return validation

class ListField:
    def __init__(self, name=None, text=None, choices=None, prompt=None, error_message=None, required=False):
        exception_message = "ListField is list or tuple of two elements value and display, or a str as value"
        self.choices = {}
        if name is None:
            raise FieldError("Field name is required")
        self.name = name
        self.text = text or name
        self.prompt = prompt
        self.error_message = error_message
        self.required = required
        index = 1
        for choice in choices:
            if isinstance(choice, (list, tuple)):
                if len(choice) != 2:
                    raise FieldError(exception_message)
                self.choices[index] = {"value": choice[0], "display": choice[1]}
            elif isinstance(choice, str):
                self.choices[index] = {"value": choice, "display": choice}
            else:
                raise FieldError(exception_message)
            index += 1

    def ask(self, question=None, error_message=None, prompt=None):
        error_message = self.error_message or error_message
        print(f"{self.text}{'*' if self.required else ''}")
        for choice in self.choices:
            print(f"{choice:<5}- {self.choices[choice]['display']}")
        response = Field(
            name="response", text=" ", typing=int, required=self.required, validator=lambda x: x in self.choices,
            prompt=prompt, error_message=error_message).ask()
        return self.choices[response]["value"] if response else None

class Form:
    def __init__(self, fields: list = None, validator=None, error_message=None, prompt=PROMPT, update_choice_error_message="Invalid choice"):
        self.fields = fields
        self.validator = validator
        self.error_message = error_message
        self.prompt = prompt or PROMPT
        self.update_choice_error_message = update_choice_error_message

    def add_fields(self, fields):
        for field in fields:
            self.add_field(field)

    def add_field(self, field):
        self.fields.append(field)

    def ask(self):
        confirmed = False
        while confirmed is False:
            confirmed = True
            data = {}
            for field in self.fields:
                if isinstance(field, TextField):
                    print(field)
                    continue
                if field.name in data:
                    raise FormError(f"Field {field.name} already exists")
                if not isinstance(field, (Field, ListField)):
                    raise FormError("Field must be a Field or ListField")
                if isinstance(field, Field):
                    question = field.text or field.name
                    data[field.name] = field.ask(question, field.error_message or self.error_message, field.prompt or self.prompt)
                elif isinstance(field, ListField):
                    data[field.name] = field.ask(field.name, field.error_message or self.error_message, field.prompt or self.prompt)
        return data

    def update(self, data=None, exclude=list(), yes_update=("y", "yes"), set_null=("n", "null"), end=("e", "end"), next=("", "next"),
               message="Update"):
        data = data
        for field in self.fields:
            if field.name in data and field.name not in exclude:
                default = data[field.name]
                response_is_correct = False
                while response_is_correct is False:
                    response_is_correct = True
                    response = input(
                        f"{message} '{field.name}'[{default}] {yes_update[1]}({yes_update[0].lower() or 'ENTER'})/{set_null[1]}({set_null[0].lower() or 'ENTER'})/"
                        f"{end[1]}({end[0].lower() or 'ENTER'})/{next[1]}({next[0].lower() or 'ENTER'})?{self.prompt}").lower().strip()

                    if response == yes_update[0].lower():
                        question = field.text or field.name
                        data[field.name] = field.ask()
                    elif response == set_null[0].lower():
                        if not field.required:
                            data[field.name] = None
                        else:
                            print(field.error_message)
                            response_is_correct = False
                    elif response == end[0].lower():
                        return data
                    elif response == next[0].lower():
                        continue
                    else:
                        response_is_correct = False
                        print(f"{self.update_choice_error_message}")
        return data


class MenuItem:
    def __init__(self, key: str|int=None, label: str="", callback: Callable|None=None, *args, **kwargs):
        if key is None:
            raise FieldError("Key is required for MenuItem")
        if callback is None:
            raise FieldError("Callback is required for MenuItem")
        self.key = str(key)
        self.label = label
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        self.callback(*self.args, **self.kwargs)

    def __str__(self):
        return f"<MenuItem: {self.label}-{self.callback}>"


class Menu:
    def __init__(self, items=None, title="Menu", prompt=PROMPT, width=WIDTH, error_message="Invalid choice", clear_on_error=False):
        """Labels are a list or tuple of 3 elements: [key, label, callback]"""
        self.title = title
        self.prompt = prompt
        self.width = width
        self.error_message = error_message
        self.clear_on_error = clear_on_error
        self.items = {}
        self.messages = []
        if items:
            self.add_items(items)

    def add_items(self, items):
        for item in items:
            self.add_item(item)

    def add_item(self, item: tuple|list|MenuItem):
        if isinstance(item, MenuItem):
            self.items[str(item.key)] = item
            return
        try:
            item = MenuItem(*item)
        except Exception as e:
            raise FieldError(f"Invalid menu item: {e}")
        self.items[item.key] = item

    def ask(self, error=None):
        display = f"\n=== {self.title} " + "="*(self.width - len(self.title) - 5) + "\n"
        buttons = []
        buttons_line = "|"
        for key in self.items:
            item = self.items[key]
            buttons.append(f"{item.key}: {item.label}")
        for button in buttons:
            if len(buttons_line) + len(button) > self.width - 5:
                display += buttons_line + "\n" + "-"*(self.width) + "\n"
                buttons_line = "|"
            buttons_line += button + " | "
        display += buttons_line + "\n" + "="*(self.width) + "\n"
        display += error or ''
        print(display)
        while len(self.messages) > 0:
            print(self.messages.pop(0))
        value = input(self.prompt or PROMPT)
        if value in self.items:
            item = self.items[value]
            item.callback(*item.args, **item.kwargs)
        else:
            if self.clear_on_error:
                clear()
            return self.ask(self.error_message)

class AutoArray:
    """Build quickly an array of datas, the only required parameter is a list of dictionaries
    containing only strings, integers or booleans"""
    def __init__(self, liste, title=None, color_1=None, color_2=None, exclude=None, include=None, width=WIDTH):
        self.liste = liste
        self.as_string = ""
        if include is not None and exclude is not None:
            raise FieldError("You can't have both include and exclude set", "Internal")
        if not isinstance(liste, list):
            raise FieldError("Array must be a list of dictionaries")
        if title is not None:
            title = f"{'='*3} {title} "
            self.as_string += f"{title:=<{width}}\n"
        if len(liste) == 0:
            self.as_string += f"{'--- No data recorded ---':^{width}}\n"
            return
        if include is not None:
            keys_nbr = len(include)
        elif exclude is not None:
            keys_nbr = len(liste[0]) - len(exclude)
        else:
            keys_nbr = len(liste[0])
        header_bar = f"{'index':<6}"
        if include is not None:
            for key in include:
                header_bar += f"{key.title():<{(width-6) // keys_nbr}}"
        else:
            for key in liste[0]:
                if exclude and key in exclude:
                    continue
                header_bar += f"{key.title():<{(width-6) // keys_nbr}}"
        self.as_string += f"{header_bar}\n" + "-"*width + "\n"
        for i in range(len(liste)):
            line = ""
            color_1 = color_1 or ''
            color_2 = color_2 or ''
            color = color_1 if i % 2 == 0 else color_2
            self.as_string += f"{color}"
            line = f"{i:<6}"
            if include is not None:
                for key in include:
                    display = liste[i][key] if liste[i][key] is not None else "-"
                    line += f"{display:<{(width-6) // keys_nbr}}"
            else:
                for key in liste[i]:
                    if include and key not in include:
                        continue
                    if exclude and key in exclude:
                        continue
                    display = liste[i][key] if liste[i][key] is not None else "-"
                    line += f"{display:<{(width-6) // keys_nbr}}"
            line += " " * (width - len(line))
            self.as_string += line
            self.as_string += f"\x1b[0m"  # end color
            self.as_string += f"\n"

    def __str__(self):
        return self.as_string

    def get(self, index: int):
        if index < len(self.liste) and index >= 0:
            return self.liste[index]
        return None
