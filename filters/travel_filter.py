from aiogram.filters import Filter
from aiogram.types import Message

from utils import check_travel_exist


class TitleNotExist(Filter):
    async def __call__(self, message: Message) -> bool:
        return not check_travel_exist(message.text, message.from_user.id)


class TitleExist(Filter):
    async def __call__(self, message: Message) -> bool:
        return check_travel_exist(message.text, message.from_user.id)
