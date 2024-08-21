from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from models import base
from models.travels import Travel

router = Router()


@router.callback_query(F.data.startswith("are_you_sure_"))
async def are_you_sure(callback: CallbackQuery):
    await callback.answer()
    data = callback.data.replace('are_you_sure_', '')
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Да', callback_data=data))
    builder.add(InlineKeyboardButton(text='Нет', callback_data='my_travels_0'))
    await callback.message.answer('Ты уверен, что хочешь удалить?',
                                  reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("del_travel_"))
async def delete_travel(callback: CallbackQuery):
    await callback.answer()
    travel_id = int(callback.data.replace("del_travel_", ''))
    with Session(base.engine) as session:
        travel = session.query(Travel).filter_by(id=int(travel_id)).first()
        session.delete(travel)
        session.commit()
    await callback.message.answer(f'Путешествие №{travel_id} успешно удалено',
                                  reply_markup=ReplyKeyboardRemove())
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Вернуться', callback_data='my_travels_0'))
    await callback.message.answer('К путешествиям', reply_markup=builder.as_markup())
