import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from models import base
from models.travels import Location
from utils import get_weather

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith("view_weather_"))
async def view_weather(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    travel_id = int(callback.data.replace("view_weather_", ''))
    try:
        await callback.message.answer('Обновляю погоду...', reply_markup=ReplyKeyboardRemove())
        with Session(base.engine) as session:
            locations = session.query(Location).filter_by(travel_id=int(travel_id)).order_by(Location.date_start).all()
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
            weather_text = ''
            for n, location in enumerate(locations):
                weather = await get_weather((location.lat, location.long))
                weather_text += f'<b>{n + 1}. {location.city}, {location.country}</b>\n'
                weather_text += f'{weather}\n---------\n'
        await callback.message.answer(weather_text, reply_markup=builder.as_markup())
    except Exception as e:
        logger.critical('Weather: %s', e)
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        await callback.message.answer('К сожалению, у меня не получилось загрузить погоду для тебя :(',
                                      reply_markup=builder.as_markup())
