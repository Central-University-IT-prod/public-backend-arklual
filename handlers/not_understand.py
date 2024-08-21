from aiogram import Router
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message()
async def not_under_mes(message: Message):
    await message.answer(
        'Ой, ты ввёл что-то не то. Попробуй снова. Если ты хочешь вернуться в главное меню нажми /main_menu')


@router.callback_query()
async def not_under_call(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('Ой, ты нажал не туда. Нажми сюда -> /main_menu')
