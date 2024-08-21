from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


def get():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Изменить имя", callback_data="profile_change_first_name"
        ),
        types.InlineKeyboardButton(
            text="Изменить фамилию", callback_data="profile_change_last_name"
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Изменить bio", callback_data="profile_change_bio"
        ),
        types.InlineKeyboardButton(
            text="Изменить геолокацию", callback_data="profile_change_location"
        ),
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Изменить возраст", callback_data="profile_change_age"
        ),
        types.InlineKeyboardButton(text="В главное меню", callback_data="main_menu"),
    )
    return builder.as_markup()
