from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.orm import Session

from models import base
from models.travels import Location
from utils import find_hotels

router = Router()


@router.callback_query(F.data.startswith('hotels_choose_loc_'))
async def hotels_choose_loc(callback: CallbackQuery):
    travel_id = callback.data.replace('hotels_choose_loc_', '')
    await callback.answer()
    with Session(base.engine) as session:
        locations = session.query(Location).filter_by(travel_id=int(travel_id)).order_by(Location.date_start).all()
        builder = InlineKeyboardBuilder()
        for location in locations:
            builder.row(InlineKeyboardButton(text=f'{location.country}, {location.city}',
                                             callback_data=f'hotels_view_{location.id}_0'))
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        await callback.message.edit_text('Выбери место', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("hotels_view_"))
async def hotels_view(callback: CallbackQuery):
    location_id, page = callback.data.replace('hotels_view_', '').split('_')
    page = int(page)
    await callback.answer()
    await callback.message.answer('Загрузка...', reply_markup=ReplyKeyboardRemove())
    with Session(base.engine) as session:
        location = session.query(Location).filter_by(id=int(location_id)).first()
        builder = InlineKeyboardBuilder()
        node = (location.lat, location.long)
        hotels = await find_hotels(node)
        print(hotels)
        if len(hotels) == 0:
            builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{location.travel_id}'))
            await callback.message.answer('В этом месте нет отелей', reply_markup=builder.as_markup())
            return
        answer = f'<b>{hotels[page]["title"]}</b>\nГород: {hotels[page]["city"]}\nАдрес: {hotels[page]["address"]}'
        if hotels[page].get('rating', None):
            answer += f"\nРейтинг: {hotels[page].get('rating', 'нет данных')}"
        if page != 0:
            builder.add(InlineKeyboardButton(text='<--', callback_data=f'hotels_view_{location_id}_{page - 1}'))
        if page + 1 != len(hotels):
            builder.add(InlineKeyboardButton(text='-->', callback_data=f'hotels_view_{location_id}_{page + 1}'))
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{location.travel_id}'))
        if hotels[page].get('images', []):
            try:
                media_group = MediaGroupBuilder(caption=answer)
                for i in hotels[page].get('images', [])[:10]:
                    media_group.add_photo(media=i)
                await callback.message.answer_media_group(media_group.build())
                await callback.message.answer('Меню', reply_markup=builder.as_markup())
            except TelegramBadRequest:
                await callback.message.answer(answer, reply_markup=builder.as_markup())
        else:
            await callback.message.answer(answer, reply_markup=builder.as_markup())
