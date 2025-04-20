import re
from telebot import types

def made_buttons(*args) -> list:

    buttons = [types.KeyboardButton(x) for x in args]
    return buttons


def text_validate(text, mode):

    if mode == "add_word_EN":
        return text.isalpha() and text.isascii()
    if mode == "add_word_RU":
        return bool(re.fullmatch(r'[А-Яа-яёЁ]+', text))