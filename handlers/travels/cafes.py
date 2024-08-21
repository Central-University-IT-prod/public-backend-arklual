from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from models import base
from models.travels import Location
from utils import find_cafes

router = Router()


@router.callback_query(F.data.startswith('cafes_choose_loc_'))
async def cafes_choose_loc(callback: CallbackQuery):
    travel_id = callback.data.replace('cafes_choose_loc_', '')
    await callback.answer()
    with Session(base.engine) as session:
        locations = session.query(Location)\
            .filter_by(travel_id=int(travel_id))\
            .order_by(Location.date_start).all()
        builder = InlineKeyboardBuilder()
        for location in locations:
            builder.row(InlineKeyboardButton(text=f'{location.country}, {location.city}',
                                             callback_data=f'cafes_view_{location.id}'))
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        await callback.message.edit_text('Выбери место', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("cafes_view_"))
async def cafes_view(callback: CallbackQuery):
    location_id = callback.data.replace('cafes_view_', '')
    await callback.answer()
    await callback.message.answer('Загрузка...', reply_markup=ReplyKeyboardRemove())
    with Session(base.engine) as session:
        location = session.query(Location)\
            .filter_by(id=int(location_id)).first()
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Назад',
                                         callback_data=f'view_travel_{location.travel_id}'))
        node = (location.lat, location.long)
        cafes = await find_cafes(node)
        if len(cafes) == 0:
            await callback.message.answer('В этом месте нет кафе и рестаранов',
                                          reply_markup=builder.as_markup())
            return
    answer = 'Ты можешь поесть здесь:'
    for n, cafe in enumerate(cafes):
        if len(answer+f'\n\n{n + 1}. <b>{cafe["title"]}</b>\nГород: {cafe["city"]}\nАдрес: {cafe["address"]}\nРейтинг: 5\nЦены: очень дорогие')<4096:
            answer += f'\n\n{n + 1}. <b>{cafe["title"]}</b>\nГород: {cafe["city"]}\nАдрес: {cafe["address"]}'
        else:
            await callback.message.answer(answer)
            answer = f'\n\n{n + 1}. <b>{cafe["title"]}</b>\nГород: {cafe["city"]}\nАдрес: {cafe["address"]}'
        if cafe.get('rating', None):
            answer += f"\nРейтинг: {cafe.get('rating', 'нет данных')}"
        if cafe.get('price', None) and str(cafe.get('price', '')).isdigit():
            if int(cafe.get('price', 0)) == 1:
                answer += "\nЦены: дешёвые"
            elif int(cafe.get('price', 0)) == 1:
                answer += "\nЦены: умеренные"
            elif int(cafe.get('price', 0)) == 1:
                answer += "\nЦены: дорогие"
            elif int(cafe.get('price', 0)) == 1:
                answer += "\nЦены: очень дорогие"
    await callback.message.answer(answer, reply_markup=builder.as_markup())
