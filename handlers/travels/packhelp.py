import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

import ai
from models import base
from models.travels import Location
from models.users import User
from utils import get_weather

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith("pack_help_"))
async def gendered_pack_help(callback: CallbackQuery):
    await callback.answer()
    travel_id = callback.data.replace('pack_help_', '')
    with Session(base.engine) as session:
        user = session.query(User).filter_by(telegram_id=int(callback.from_user.id)).first()
        gender = 'man' if user.is_male else 'woman'
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Работа/учёба',
                                     callback_data=f'categorized_gendered_pack_help_work_{gender}_{travel_id}'))
    builder.row(
        InlineKeyboardButton(text='Отдых', callback_data=f'categorized_gendered_pack_help_rest_{gender}_{travel_id}'))
    await callback.message.edit_text('Выберите цель путешествия:', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("categorized_gendered_pack_help_"))
async def categorized_gendered_pack_help(callback: CallbackQuery):
    await callback.answer()
    wait_message = await callback.message.answer('Загрузка...')
    category, gender, travel_id = callback.data.replace('categorized_gendered_pack_help_', '').split('_')
    with Session(base.engine) as session:
        locations = session.query(Location).filter_by(travel_id=int(travel_id)).order_by(Location.date_start).all()
        me = session.query(User).filter_by(telegram_id=int(callback.from_user.id)).first()
        weather_text = ''
        for n, location in enumerate(locations):
            weather = await get_weather((location.lat, location.long))
            weather_text += f'<b>{n + 1}. {location.city}, {location.country}</b>\n'
            weather_text += f'{weather}\n---------\n'
        is_man = False
        if gender == 'man':
            is_man = True
        to_rest = False
        if category == 'rest':
            to_rest = True
        days = (locations[-1].date_end - locations[0].date_start).days
        try:
            help_data = await ai.pack_help(is_man, me.age, to_rest, days, weather_text)
        except Exception as e:
            logger.critical('Pack help: %s', e)
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
            await callback.message.edit_text('К сожалению, не могу помочь с этим путешествием :(',
                                             reply_markup=builder.as_markup())
            return
        answer = 'Мне кажется, тебе нужно взять:\n'
        for n, i in enumerate(help_data):
            answer += f'\n{n + 1}. {i["type"]}: '
            for k, j in enumerate(i['things']):
                answer += f'\n  {k + 1}) {j["name"]} x{j["count"]}'
        await wait_message.delete()
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        await callback.message.edit_text(answer, reply_markup=builder.as_markup())
