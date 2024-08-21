from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from utils import check_user_exist

class Unregistered(Filter):
    async def __call__(self, message: Message) -> bool:
        return not check_user_exist(message.from_user.id)

class Registered(Filter):
    async def __call__(self, message: Message) -> bool:
        return check_user_exist(message.from_user.id)

class RegisteredCallback(Filter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        return check_user_exist(callback.from_user.id)