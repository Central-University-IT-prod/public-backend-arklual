from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)

def make_column_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    column = [[KeyboardButton(text=item)] for item in items]
    return ReplyKeyboardMarkup(keyboard=column, resize_keyboard=True)
