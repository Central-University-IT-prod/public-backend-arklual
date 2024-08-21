from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

import strings
from filters.user_filter import Registered, Unregistered
from handlers.main_menu import command_main_menu_handler
from keyboards import share_position, add_interests
from models import base, users
from utils import get_city, get_country


class UserRegistration(StatesGroup):
    first_name = State()
    last_name = State()
    bio = State()
    location = State()
    gender = State()
    age = State()


class AddInterest(StatesGroup):
    interest = State()


router = Router()


@router.message(CommandStart(), Registered())
async def command_start_handler_reg(message: Message, state: FSMContext):
    await state.clear()
    await command_main_menu_handler(message, state)


@router.message(CommandStart())
@router.message(Command('main_menu'), Unregistered())
async def command_start_handler(message: Message, state: FSMContext):
    await state.set_state(UserRegistration.first_name)
    await message.answer(strings.WELOCOME, reply_markup=ReplyKeyboardRemove())


@router.message(UserRegistration.first_name, F.text.len() <= 255)
async def first_name_entered(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text.capitalize())
    await message.answer(
        text=strings.REGISTRATION_FIRST_NAME_ENTERED,
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(UserRegistration.last_name)


@router.message(UserRegistration.first_name, F.text)
async def first_name_entered_invalid(message: Message, state: FSMContext):
    await message.answer(
        text="Длина имени должна быть не больше 255 символов",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(UserRegistration.first_name)


@router.message(UserRegistration.last_name, F.text.len() <= 255)
async def last_name_entered(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text.capitalize())
    await message.answer(
        text=strings.REGISTRATION_LAST_NAME_ENTERED,
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(UserRegistration.bio)


@router.message(UserRegistration.last_name, F.text)
async def last_name_entered_invalid(message: Message, state: FSMContext):
    await message.answer(
        text="Длина фамилии должна быть не больше 255 символов",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(UserRegistration.last_name)


@router.message(UserRegistration.bio, F.text)
async def bio_entered(message: Message, state: FSMContext):
    await state.update_data(bio=message.text)
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Мужской', callback_data='gender_chosen_male'),
                InlineKeyboardButton(text='Женский', callback_data='gender_chosen_female'))
    await message.answer(
        text=strings.REGISTRATION_BIO_ENTERED,
        reply_markup=builder.as_markup()
    )
    await state.set_state(UserRegistration.gender)


@router.callback_query(UserRegistration.gender, F.data.startswith('gender_chosen_'))
async def gender_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    gender = callback.data.replace('gender_chosen_', '')
    await state.update_data(gender=gender)
    await callback.message.answer(
        text=strings.REGISTRATION_GENDER_ENTERED,
        reply_markup=share_position.get()
    )
    await state.set_state(UserRegistration.location)


@router.message(UserRegistration.location, F.location)
async def country_chosen_valid(message: Message, state: FSMContext):
    await state.update_data(location=(message.location.latitude, message.location.longitude))
    await message.answer(
        text=strings.REGISTRATION_VALID_COUNTRY_ENTERED,
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(UserRegistration.age)


@router.message(UserRegistration.location, F.web_app_data)
async def country_chosen_valid_webapp(message: Message, state: FSMContext):
    data = message.web_app_data.data
    try:
        lat, long, city, country = data.split('|')
        if str(lat) == '' or str(long) == '' or str(city) == '' or str(country) == '':
            raise ValueError()
    except:
        await country_chosen_invalid(message, state)
        return
    try:
        await state.update_data(location=(lat, long))
        await state.update_data(location_named=(city, country))
    except:
        await country_chosen_invalid(message, state)
        return
    await message.answer(
        text=strings.REGISTRATION_VALID_COUNTRY_ENTERED,
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(UserRegistration.age)


@router.message(UserRegistration.location)
async def country_chosen_invalid(message: Message, state: FSMContext):
    await message.answer(
        text=strings.REGISTRATION_INVALID_COUNTRY_ENTERED,
        reply_markup=share_position.get()
    )
    await state.set_state(UserRegistration.location)


@router.message(UserRegistration.age, F.text.regexp(r'^[0-9]*$'))
async def age_entered_valid(message: Message, state: FSMContext):
    if int(message.text) > 250:
        await age_entered_invalid(message, state)
        return
    await state.update_data(age=message.text)
    data = await state.get_data()
    await state.clear()
    tmp_message = await message.answer('Записываю тебя, подожди пару секунд', reply_markup=ReplyKeyboardRemove())
    with Session(base.engine) as session:
        lat, long = data['location']
        city, country = data.get('location_named', (None, None))
        if not city:
            city = get_city(lat, long)
        if not country:
            country = get_country(lat, long)
        is_male = True if data.get('gender', 'female') == 'male' else False
        new_user = users.User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            bio=data['bio'],
            country=country,
            city=city,
            lat=float(lat),
            long=float(long),
            age=data['age'],
            looking_for_a_partner=True,
            is_male=is_male,
            telegram_id=int(message.from_user.id)
        )
        session.add(new_user)
        session.commit()
    await tmp_message.delete()
    await state.set_state(AddInterest.interest)
    await message.answer(
        text=strings.REGISTRATION_VALID_AGE_ENTERED,
        reply_markup=add_interests.get()
    )


@router.message(UserRegistration.age)
async def age_entered_invalid(message: Message, state: FSMContext):
    await message.answer(
        text=strings.REGISTRATION_INVALID_AGE_ENTERED,
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(UserRegistration.age)


@router.callback_query(AddInterest.interest, F.data.startswith('user_registration_interest_'))
async def interest_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    interest_id = callback.data.replace('user_registration_interest_', '')
    interest_title = strings.INTERESTS[int(interest_id)]
    with Session(base.engine) as session:
        new_interest = users.Interest(
            user_id=callback.from_user.id,
            title=interest_title
        )
        session.add(new_interest)
        session.commit()
        all_interests = session.query(users.Interest).filter_by(user_id=callback.from_user.id).all()
        odds = []
        for i in all_interests:
            odds.append(str(i.title))
    await state.set_state(AddInterest.interest)
    answer = 'Твои интересы:'
    for n, i in enumerate(odds):
        answer += f'\n{n + 1}. {i}'
    await callback.message.answer(
        text=answer,
    )
    await callback.message.answer(
        text=strings.REGISTRATION_INTEREST_ENTERED,
        reply_markup=add_interests.get(odd=odds)
    )


@router.callback_query(AddInterest.interest, F.data == 'user_registration_finish')
async def user_registration_finish(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(strings.END_REGISTRATION, reply_markup=ReplyKeyboardRemove())
