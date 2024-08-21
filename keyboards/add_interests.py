from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import strings

def get(odd=None):
    builder = InlineKeyboardBuilder()
    row = []
    odd = odd if odd is not None else []
    for i, interest in enumerate(strings.INTERESTS):
        if interest not in odd:
            row.append(InlineKeyboardButton(text=interest,
                                            callback_data=f"user_registration_interest_{i}"))
            if (i+1) % 2 == 0:
                builder.row(*row)
                row = []
    builder.row(InlineKeyboardButton(text='Завершить', callback_data='user_registration_finish'))
    return builder.as_markup()
