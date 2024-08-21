from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from handlers.travels.fsm import CreateLocation
from models import base
from models.travels import Travel, TravelPartner, Location

router = Router()


@router.callback_query(F.data.startswith("view_travel_"))
async def view_travels(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    travel_id = int(callback.data.replace("view_travel_", ''))
    with Session(base.engine) as session:
        travel = session.query(Travel).filter_by(id=int(travel_id)).first()
        locations = session.query(Location).filter_by(travel_id=int(travel_id)).order_by(Location.date_start).all()
        locs_str = 'Места:'
        for n, loc in enumerate(locations):
            locs_str += f'\n{n + 1}. {loc.city} с {loc.date_start} по {loc.date_end}'
        await state.set_state(CreateLocation.location)
        await state.update_data(travel_id=travel.id)
        await state.update_data(title=travel.title)
        btn = KeyboardButton(text="Добавить место", web_app=WebAppInfo(url='https://arklual.github.io/prod3_webapp1/'))
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btn]], one_time_keyboard=True)
        last_id = (await callback.message.answer(locs_str, reply_markup=keyboard)).message_id
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text='Удалить путешествие', callback_data=f'are_you_sure_del_travel_{travel_id}'))
        builder.row(InlineKeyboardButton(text='Удалить место', callback_data=f'del_choose_location_{travel_id}'),
                    InlineKeyboardButton(text='Заметки', callback_data=f'view_notes_{travel_id}_0'))
        builder.row(InlineKeyboardButton(text='Изменить название', callback_data=f'alter_travel_title_{travel_id}'),
                    InlineKeyboardButton(text='Изменить описание', callback_data=f'alter_travel_desc_{travel_id}'))
        builder.row(InlineKeyboardButton(text='На карте', callback_data=f'view_map_{travel_id}'),
                    InlineKeyboardButton(text='На карте от меня', callback_data=f'view_me_map_{travel_id}'), )
        builder.row(InlineKeyboardButton(text='Мои спутники', callback_data=f'view_trav_partners_{travel_id}'),
                    InlineKeyboardButton(text='Добавить спутника', callback_data=f'add_travel_partner_{travel_id}'))
        builder.row(InlineKeyboardButton(text='Узнать погоду', callback_data=f'view_weather_{travel_id}'),
                    InlineKeyboardButton(text='Что посетить?', callback_data=f'attrations_choose_location_{travel_id}'))
        builder.row(InlineKeyboardButton(text='Где поесть?', callback_data=f'cafes_choose_loc_{travel_id}'),
                    InlineKeyboardButton(text='Выбрать отель', callback_data=f'hotels_choose_loc_{travel_id}'))
        tmp_partners = session.query(TravelPartner).filter_by(travel_id=int(travel.id)).all()
        author = travel.user_id
        partners = []
        for partner in tmp_partners:
            partners.append(int(partner.user_id))
        if author not in partners:
            partners.append(author)
        if callback.from_user.id in partners:
            partners.remove(callback.from_user.id)
        if len(partners) > 0:
            builder.row(InlineKeyboardButton(text='Совместные траты', callback_data=f'splitwise_{travel_id}'))
        if not travel.is_archived:
            builder.row(InlineKeyboardButton(text='Помощь со сбором', callback_data=f'pack_help_{travel_id}'))
        back_link = 'my_archive_travels_0' if travel.is_archived else 'my_travels_0'
        archive_text = 'Разахивировать' if travel.is_archived else 'Архивировать'
        builder.row(InlineKeyboardButton(text=archive_text, callback_data=f'archive_{travel_id}'))
        builder.row(InlineKeyboardButton(text='Назад', callback_data=back_link))
        await callback.message.answer(f"""
ID: {travel_id}
Название: {travel.title}
Описание: {travel.description}
""", reply_markup=builder.as_markup())

        attemp = 0
        for i in range(last_id - 1, -1, -1):
            if attemp == 3:
                break
            try:
                await callback.bot.delete_message(callback.from_user.id, i)
            except:
                attemp += 1


@router.callback_query(F.data.startswith("archive_"))
async def archive(callback: CallbackQuery):
    travel_id = callback.data.replace('archive_', '')
    await callback.answer()
    await callback.message.answer('Загрузка...', reply_markup=ReplyKeyboardRemove())
    with Session(base.engine) as session:
        travel = session.query(Travel).filter_by(id=int(travel_id)).first()
        travel.is_archived = not travel.is_archived
        session.commit()
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Вернуться', callback_data='my_travels_0'))
    await callback.message.answer('К путешествиям', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("del_choose_location_"))
async def del_choose_location(callback: CallbackQuery):
    travel_id = callback.data.replace('del_choose_location_', '')
    await callback.answer()
    builder = InlineKeyboardBuilder()
    with Session(base.engine) as session:
        locations = session.query(Location).filter_by(travel_id=int(travel_id)).order_by(Location.date_start).all()
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        if len(locations) <= 2:
            await callback.message.edit_text('Чтобы удалить место, их должно быть хотя бы 3',
                                             reply_markup=builder.as_markup())
            return
        for location in locations:
            builder.row(InlineKeyboardButton(text=f'{location.country}, {location.city}',
                                             callback_data=f'del_location_{location.id}'))
        await callback.message.edit_text('Выбери место', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("del_location_"))
async def del_location(callback: CallbackQuery):
    location_id = callback.data.replace('del_location_', '')
    await callback.answer()
    with Session(base.engine) as session:
        location = session.query(Location).filter_by(id=int(location_id)).first()
        location_id = int(location.travel_id)
        session.delete(location)
        session.commit()
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{location_id}'))
        await callback.message.edit_text('Успешно удалено!', reply_markup=builder.as_markup())
