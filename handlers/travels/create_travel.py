from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, \
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types.web_app_info import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dateutil import parser
from sqlalchemy.orm import Session

from filters.travel_filter import TitleExist, TitleNotExist
from handlers.travels.fsm import CreateTravel, CreateLocation
from models import base
from models.travels import Travel, Location
from utils import check_if_locations_too_few

router = Router()


@router.callback_query(F.data == "create_travel")
async def create_travel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введи название путешествия', reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateTravel.title)


@router.message(CreateTravel.title, F.text.len() > 255)
async def title_invalid(message: Message, state: FSMContext):
    await message.answer('Введи, пожалуйста, более короткое название путешествия',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateTravel.title)


@router.message(CreateTravel.title, TitleExist())
async def title_invalid1(message: Message, state: FSMContext):
    await message.answer('У тебя уже есть путешествие с таким названием, введи, пожалуйста, другое',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateTravel.title)


@router.message(CreateTravel.title, TitleNotExist())
async def title_valid(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(CreateTravel.description)
    await message.answer('Отлично! Теперь напиши описание поездки',
                         reply_markup=ReplyKeyboardRemove())


@router.message(CreateTravel.description)
async def decription_entered(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    with Session(base.engine) as session:
        travel = Travel(
            title=data['title'],
            description=data['description'],
            user_id=int(message.from_user.id),
            is_archived=False
        )
        session.add(travel)
        session.commit()
        await state.clear()
        await state.set_state(CreateLocation.location)
        await state.update_data(travel_id=travel.id)
        await state.update_data(title=data['title'])
    btn = KeyboardButton(text="Добавить место",
                         web_app=WebAppInfo(
                             url='https://arklual.github.io/prod3_webapp1/'))
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btn]], one_time_keyboard=True)
    await message.answer(f'{data["title"]}\nМеста, которые я посещу:', reply_markup=keyboard)


@router.message(CreateLocation.location, F.web_app_data)
async def location_handler(message: Message, state: FSMContext):
    travel_id = (await state.get_data())['travel_id']
    data = message.web_app_data.data
    try:
        country, city, lat, long, start_date, end_date = data.split('|')
        if str(country) == '' or str(city) == '' or str(lat) == '' or str(long) == '':
            raise ValueError()
    except Exception:
        btn = KeyboardButton(text="Добавить место",
                             web_app=WebAppInfo(
                                 url='https://arklual.github.io/prod3_webapp1/'))
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btn]], one_time_keyboard=True)
        await message.answer('Ты что-то заполнил не все поля, попробуй снова', reply_markup=keyboard)
        await state.set_state(CreateLocation.location)
        return
    try:
        start_date = start_date.split()[0] + ' ' + start_date.split()[1] + ' ' + start_date.split()[2] + ' ' + \
                     start_date.split()[3]
        end_date = end_date.split()[0] + ' ' + end_date.split()[1] + ' ' + end_date.split()[2] + ' ' + end_date.split()[
            3]
        start_date = parser.parse(start_date)
        end_date = parser.parse(end_date)
    except:
        await state.set_state(CreateLocation.location)
        btn = KeyboardButton(text="Добавить место",
                             web_app=WebAppInfo(url='https://arklual.github.io/prod3_webapp1/'))
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btn]], one_time_keyboard=True)
        await message.answer('Ты ввёл некорректные даты, попробуй снова', reply_markup=keyboard)
        return
    if start_date > end_date:
        await state.set_state(CreateLocation.location)
        btn = KeyboardButton(text="Добавить место",
                             web_app=WebAppInfo(url='https://arklual.github.io/prod3_webapp1/'))
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                       keyboard=[[btn]], one_time_keyboard=True)
        await message.answer('Ты ввёл дату приезда позже, чем дату выезда! Добавь место заново',
                             reply_markup=keyboard)
        return
    try:
        with Session(base.engine) as session:
            other_locations = session.query(Location).filter_by(travel_id=int(travel_id)).order_by(
                Location.date_start).all()
            for loc in other_locations:
                if loc.date_start <= start_date.date() < loc.date_end or loc.date_start < end_date.date() <= loc.date_end or \
                        start_date.date() <= loc.date_start < end_date.date() or start_date.date() < loc.date_end <= end_date.date():
                    await state.set_state(CreateLocation.location)
                    btn = KeyboardButton(text="Добавить место",
                                         web_app=WebAppInfo(url='https://arklual.github.io/prod3_webapp1/'))
                    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btn]], one_time_keyboard=True)
                    await message.answer('Ты не можешь находиться в двух местах одновременно! Добавь место заново',
                                         reply_markup=keyboard)
                    return
            location = Location(
                country=country,
                city=city,
                lat=float(lat),
                long=float(long),
                date_start=start_date,
                date_end=end_date,
                travel_id=int(travel_id)
            )
            session.add(location)
            session.commit()
    except Exception as e:
        print(e)
        btn = KeyboardButton(text="Добавить место", web_app=WebAppInfo(url='https://arklual.github.io/prod3_webapp1/'))
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btn]], one_time_keyboard=True)
        await message.answer('Ты что-то неправильно ввёл, попробуй снова', reply_markup=keyboard)
        await state.set_state(CreateLocation.location)
        return
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Завершить создание', callback_data=f'finish_locations_{travel_id}'))
    btn = KeyboardButton(text="Добавить место", web_app=WebAppInfo(url='https://arklual.github.io/prod3_webapp1/'))
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btn]], one_time_keyboard=True)
    data = await state.get_data()
    await message.answer(data["title"], reply_markup=builder.as_markup())
    answ = 'Места, которые я посещу:\n'
    with Session(base.engine) as session:
        locations = session. \
            query(Location.city, Location.country, Location.date_start, Location.date_end). \
            filter_by(travel_id=int(travel_id)).order_by(Location.date_start).all()
    for n, i in enumerate(locations):
        city, country, date_start, date_end = i
        answ += f'\n{n + 1}. {city}, {country} с {date_start} по {date_end}'
    await message.answer(answ, reply_markup=keyboard)


@router.message(CreateLocation.location)
async def location_handler_invalid(message: Message, state: FSMContext):
    btn = KeyboardButton(text="Добавить место", web_app=WebAppInfo(url='https://arklual.github.io/prod3_webapp1/'))
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btn]], one_time_keyboard=True)
    await message.answer('Ты должен отправить место именно через кнопку, попробуй снова', reply_markup=keyboard)
    await state.set_state(CreateLocation.location)


@router.callback_query(F.data.startswith('finish_locations_'))
async def finish_locations_too_few(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    travel_id = int(callback.data.replace('finish_locations_', ''))
    if check_if_locations_too_few(travel_id):
        await state.set_state(CreateLocation.location)
        btn = KeyboardButton(text="Добавить место", web_app=WebAppInfo(url='https://arklual.github.io/prod3_webapp1/'))
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[btn]], one_time_keyboard=True)
        await callback.message.answer('Слишком мало мест, должно быть хотя бы 2. Добавь ещё', reply_markup=keyboard)
        return
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Назад', callback_data='my_travels_0'))
    await callback.message.answer('Готово!', reply_markup=builder.as_markup())
