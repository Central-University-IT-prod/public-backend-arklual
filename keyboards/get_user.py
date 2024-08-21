from aiogram import types


def get(travel_id):
    button = types.KeyboardButton(text="Отправить человека",
                                  request_user=types.KeyboardButtonRequestUser(request_id=int(travel_id)))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[button]], one_time_keyboard=True)
    return keyboard
