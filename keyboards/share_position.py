from aiogram import types
from aiogram.types.web_app_info import WebAppInfo

def get():
    button = types.KeyboardButton(text="Отправить геопозицию", request_location=True)
    button1 = types.KeyboardButton(text="Ввести вручную", web_app=WebAppInfo(url='https://arklual.github.io/prod3_webapp2/'))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[button], [button1]], one_time_keyboard=True)
    return keyboard