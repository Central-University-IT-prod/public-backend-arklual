from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from sqlalchemy.orm import Session

from filters.user_filter import RegisteredCallback
from keyboards import profile as kb
from keyboards import share_position
from models import base
from models.users import User, Interest
from utils import get_country, get_city

router = Router()


class UserAltering(StatesGroup):
    new_value = State()


async def profile(message: Message):
    with Session(base.engine) as session:
        first_name, last_name, age, country, city, bio, is_male = session. \
            query(User.first_name, User.last_name, User.age, User.country, User.city, User.bio, User.is_male). \
            filter_by(telegram_id=int(message.from_user.id)).first()
        interests = session.query(Interest).filter_by(user_id=message.from_user.id).all()
        interests_text = ''
        for n, i in enumerate(interests):
            interests_text += str(i.title).lower()
            if n + 1 != len(interests):
                interests_text += ', '
        await message.answer(f'''
Имя: {first_name}
Фамилия: {last_name}
Возраст: {age}
Страна: {country}
Город: {city}
Пол: {'Мужской' if is_male else 'Женский'}
        ''', reply_markup=ReplyKeyboardRemove())
        await message.answer(f'''
Bio:
{bio}
-----
Интересы: {interests_text}
        ''',
                             reply_markup=kb.get())


@router.callback_query(F.data == 'profile', RegisteredCallback())
async def profile_callback(callback: CallbackQuery):
    await callback.answer()
    with Session(base.engine) as session:
        first_name, last_name, age, country, city, bio, is_male = session. \
            query(User.first_name, User.last_name, User.age, User.country, User.city, User.bio, User.is_male). \
            filter_by(telegram_id=int(callback.from_user.id)).first()
        interests = session.query(Interest).filter_by(user_id=callback.from_user.id).all()
        interests_text = ''
        for n, i in enumerate(interests):
            interests_text += str(i.title).lower()
            if n + 1 != len(interests):
                interests_text += ', '
        await callback.message.answer(f'''
Имя: {first_name}
Фамилия: {last_name}
Возраст: {age}
Страна: {country}
Город: {city}
Пол: {'Мужской' if is_male else 'Женский'}
        ''', reply_markup=ReplyKeyboardRemove())
        last_id = (await callback.message.answer(f'''
Bio:
{bio}
-----
Интересы: {interests_text}
        ''',
                                                 reply_markup=kb.get())).message_id
    attemp = 0
    for i in range(last_id - 2, -1, -1):
        if attemp == 3:
            break
        try:
            await callback.bot.delete_message(callback.from_user.id, i)
        except:
            attemp += 1


@router.callback_query(F.data.startswith('profile_change_'))
async def profile_change_callback(callback: CallbackQuery, state: FSMContext):
    data = callback.data.replace('profile_change_', '')
    await callback.answer()
    await state.update_data(type=data)
    if data == 'location':
        await state.set_state(UserAltering.new_value)
        await callback.message.answer('Отправь новую геопозицию', reply_markup=share_position.get())
    else:
        await state.set_state(UserAltering.new_value)
        await callback.message.answer('Отправь новое значение', reply_markup=ReplyKeyboardRemove())


@router.message(UserAltering.new_value, F.location)
async def profile_change_location(message: Message, state: FSMContext):
    await state.clear()
    with Session(base.engine) as session:
        session.query(User). \
            filter(User.telegram_id == int(message.from_user.id)). \
            update({'country': get_country(message.location.latitude, message.location.longitude),
                    'city': get_city(message.location.latitude, message.location.longitude),
                    'lat': message.location.latitude,
                    'long': message.location.longitude})
        session.commit()
    await profile(message)


@router.message(UserAltering.new_value, F.web_app_data)
async def profile_change_location_web(message: Message, state: FSMContext):
    data = message.web_app_data.data
    try:
        lat, long, city, country = data.split('|')
        if str(lat) == '' or str(long) == '' or str(city) == '' or str(country) == '':
            raise ValueError()
    except:
        await profile_change_entered(message, state)
        return
    try:
        with Session(base.engine) as session:
            session.query(User). \
                filter(User.telegram_id == int(message.from_user.id)). \
                update({'country': country,
                        'city': city,
                        'lat': float(lat),
                        'long': float(long)})
            session.commit()
        await profile(message)
        await state.clear()
    except Exception:
        await profile_change_entered(message, state)
        return


@router.message(UserAltering.new_value, F.text)
async def profile_change_entered(message: Message, state: FSMContext):
    type_data = (await state.get_data()).get('type')
    value = message.text
    if not type_data:
        await state.clear()
        await message.answer('Ой, что-то пошло не то, попробуй снова', reply_markup=ReplyKeyboardRemove())
        await profile(message)
        return
    if type_data == 'location':
        await state.set_state(UserAltering.new_value)
        await message.answer('Ты отправил что-то не то. Отправь новую геолокацию', reply_markup=share_position.get())
        return
    elif type_data == 'age':
        if message.text.isdigit():
            value = int(message.text)
            if value > 250:
                await state.set_state(UserAltering.new_value)
                await message.answer('Возраст некорректный, отправь его снова', reply_markup=ReplyKeyboardRemove())
                return
        else:
            await state.set_state(UserAltering.new_value)
            await message.answer('Возраст некорректный, отправь его снова', reply_markup=ReplyKeyboardRemove())
            return
    elif type_data != 'bio':
        if len(message.text) > 255:
            await state.set_state(UserAltering.new_value)
            await message.answer('Слишком длинно, напиши покороче', reply_markup=ReplyKeyboardRemove())
            return
    with Session(base.engine) as session:
        session.query(User). \
            filter(User.telegram_id == int(message.from_user.id)). \
            update({type_data: value})
        session.commit()
    await state.clear()
    await profile(message)
