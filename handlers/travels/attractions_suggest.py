import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

import ai
from models import base
from models.travels import Location

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith("attrations_choose_location_"))
async def attrations_choose_location(callback: CallbackQuery):
    travel_id = callback.data.replace('attrations_choose_location_', '')
    await callback.answer()
    with Session(base.engine) as session:
        locations = session.query(Location)\
            .filter_by(travel_id=int(travel_id))\
            .order_by(Location.date_start).all()
        builder = InlineKeyboardBuilder()
        for location in locations:
            builder.row(InlineKeyboardButton(text=f'{location.country}, {location.city}',
                                             callback_data=f'attrations_view_{location.id}'))
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        await callback.message.edit_text('Выбери место', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("attrations_view_"))
async def attrations_view(callback: CallbackQuery):
    location_id = callback.data.replace('attrations_view_', '')
    await callback.answer()
    await callback.message.answer('Загрузка...', reply_markup=ReplyKeyboardRemove())
    with Session(base.engine) as session:
        location = session.query(Location)\
            .filter_by(id=int(location_id))\
            .first()
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{location.travel_id}'))
        location = str(location.city) + ', ' + str(location.country)
    try:
        recomendations = await ai.recomendate_attractions(location)
        answer = 'Ты можешь посетить:\n'
        for n, recomendation in enumerate(recomendations):
            answer += f'\n{n + 1}. <b>{recomendation["title"]}</b>\n<b>Описание:</b> {recomendation["description"]}'
        await callback.message.answer(answer, reply_markup=builder.as_markup())
    except Exception as e:
        logger.critical('Attractions: %s', e)
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Назад', callback_data='my_travels_0'))
        await callback.message.answer('Не могу ничего порекомендовать по этому путешествию :(',
                                      reply_markup=builder.as_markup())
        return
