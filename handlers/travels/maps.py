import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, ReplyKeyboardRemove, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from models import base
from models.travels import Location
from models.users import User
from utils import generate_gm_link, generate_ym_link, generate_osm_image

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith('view_map_'))
async def view_map(callback: CallbackQuery):
    await callback.answer()
    travel_id = int(callback.data.replace("view_map_", ''))
    try:
        with Session(base.engine) as session:
            locs = session.query(Location.lat, Location.long).filter_by(travel_id=travel_id).order_by(
                Location.date_start).all()
            await callback.message.answer('Подожди немного, готовлю фото карты для тебя',
                                          reply_markup=ReplyKeyboardRemove())
            yandex_link = generate_ym_link(locs)
            google_link = generate_gm_link(locs)
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text='На Яндекс Картах', url=yandex_link))
            builder.row(InlineKeyboardButton(text='На Google Maps', url=google_link))
            wait_message_2 = await callback.message.answer(
                'А пока можешь посмотреть маршрут на Яндекс Картах или Google Maps', reply_markup=builder.as_markup())
            osm_map = await generate_osm_image(locs)
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        await wait_message_2.delete()
        await callback.message.answer_photo(BufferedInputFile(osm_map, filename="map.png"),
                                            reply_markup=builder.as_markup())
    except Exception as e:
        logger.critical('Map: %s', e)
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        await callback.message.answer(
            'Не получилось составить маршрут :(. Проверь, твой маршрут должен состоять как минимум из 2 мест',
            reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('view_me_map_'))
async def view_me_map(callback: CallbackQuery):
    await callback.answer()
    travel_id = int(callback.data.replace("view_me_map_", ''))
    try:
        with Session(base.engine) as session:
            locs = session.query(Location.lat, Location.long).filter_by(travel_id=travel_id).order_by(
                Location.date_start).all()
            me_node = session.query(User.lat, User.long).filter_by(telegram_id=int(callback.from_user.id)).first()
            locs = [me_node] + locs
            await callback.message.answer('Подожди немного, готовлю фото карты для тебя',
                                          reply_markup=ReplyKeyboardRemove())
            yandex_link = generate_ym_link(locs)
            google_link = generate_gm_link(locs)
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text='На Яндекс Картах', url=yandex_link))
            builder.row(InlineKeyboardButton(text='На Google Maps', url=google_link))
            await callback.message.answer('А пока можешь посмотреть маршрут на Яндекс Картах или Google Maps',
                                          reply_markup=builder.as_markup())
            osm_map = await generate_osm_image(locs)
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        await callback.message.answer_photo(BufferedInputFile(osm_map, filename="map.png"),
                                            reply_markup=builder.as_markup())
    except Exception as e:
        logger.critical('Map: %s', e)
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        await callback.message.answer(
            'Не получилось составить маршрут :(. Проверь, твой маршрут должен состоять как минимум из 2 мест',
            reply_markup=builder.as_markup())
