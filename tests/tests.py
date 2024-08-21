import datetime

import pytest
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from unittest.mock import AsyncMock

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session

from models import base, users, travels
from utils_for_tests import TEST_CHAT, TEST_USER
from handlers import start, main_menu, not_understand, cancel
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
import strings
import utils

@pytest.mark.asyncio
async def test_unreg_start(storage, bot):
    message = AsyncMock()
    state = FSMContext(
        storage=storage,
        key=StorageKey(
            bot_id=bot.id,
            chat_id=TEST_CHAT.id,
            user_id=TEST_USER.id 
        )
    )
    await start.command_start_handler(message, state)
    message.answer.assert_called_with(strings.WELOCOME, reply_markup=ReplyKeyboardRemove())

@pytest.mark.asyncio
async def test_feedback(storage, bot):
    callback = AsyncMock()
    state = FSMContext(
        storage=storage,
        key=StorageKey(
            bot_id=bot.id,
            chat_id=TEST_CHAT.id,
            user_id=TEST_USER.id
        )
    )
    await main_menu.feedback(callback, state)
    callback.answer.assert_called()
    callback.message.answer.assert_called_with('Напиши, что хочешь передать моему разработчику')

@pytest.mark.asyncio
async def test_start(storage, bot):
    message = AsyncMock()
    state = FSMContext(
        storage=storage,
        key=StorageKey(
            bot_id=bot.id,
            chat_id=TEST_CHAT.id,
            user_id=TEST_USER.id
        )
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="💼 Мой профиль",
        callback_data="profile")
    )
    builder.row(InlineKeyboardButton(
        text="✈️ Мои путешествия",
        callback_data="my_travels_0")
    )
    builder.row(InlineKeyboardButton(
        text="⌛️ Архив путешествий",
        callback_data="my_archive_travels_0")
    )
    builder.row(InlineKeyboardButton(
        text="👨‍🦱 Найти спутников",
        callback_data="find_new_partners_0")
    )
    builder.row(InlineKeyboardButton(
        text="☎️ Обратная связь",
        callback_data="feedback")
    )
    await start.command_start_handler_reg(message, state)
    message.answer.assert_called_with(strings.MAIN_MENU, reply_markup=builder.as_markup())

@pytest.mark.asyncio
async def test_main_menu(storage, bot):
    message = AsyncMock()
    state = FSMContext(
        storage=storage,
        key=StorageKey(
            bot_id=bot.id,
            chat_id=TEST_CHAT.id,
            user_id=TEST_USER.id
        )
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="💼 Мой профиль",
        callback_data="profile")
    )
    builder.row(InlineKeyboardButton(
        text="✈️ Мои путешествия",
        callback_data="my_travels_0")
    )
    builder.row(InlineKeyboardButton(
        text="⌛️ Архив путешествий",
        callback_data="my_archive_travels_0")
    )
    builder.row(InlineKeyboardButton(
        text="👨‍🦱 Найти спутников",
        callback_data="find_new_partners_0")
    )
    builder.row(InlineKeyboardButton(
        text="☎️ Обратная связь",
        callback_data="feedback")
    )
    await main_menu.command_main_menu_handler(message, state)
    message.answer.assert_called_with(strings.MAIN_MENU, reply_markup=builder.as_markup())


@pytest.mark.asyncio
async def test_generating_yandex_link():
    result = utils.generate_ym_link([(57.222, 42.111), (59.222, 41.111)])
    assert type(result) == str
    assert result.startswith('https://')

@pytest.mark.asyncio
async def test_generating_google_link():
    result = utils.generate_gm_link([(57.222, 42.111), (59.222, 41.111)])
    assert type(result) == str
    assert result.startswith('https://')

@pytest.mark.asyncio
async def test_get_city1():
    result = utils.get_city(57.6261, 39.8845)
    assert type(result) == str
    assert result == 'Ярославль'


@pytest.mark.asyncio
async def test_get_city2():
    result = utils.get_city(57.7677, 40.9263)
    assert type(result) == str
    assert result == 'Кострома'

@pytest.mark.asyncio
async def test_get_city3():
    result = utils.get_city(57.0051, 40.9766)
    assert type(result) == str
    assert result == 'Иваново'

@pytest.mark.asyncio
async def test_get_city4():
    result = utils.get_city(48.8566, 2.3522)
    assert type(result) == str
    assert result == 'Париж'

@pytest.mark.asyncio
async def test_get_city5():
    result = utils.get_city(40.730610, -73.935242)
    assert type(result) == str
    assert result.lower() == 'нью-йорк'

@pytest.mark.asyncio
async def test_get_city6():
    result = utils.get_city(56.3269, 44.0059)
    assert type(result) == str
    assert result == 'Нижний Новгород'

@pytest.mark.asyncio
async def test_get_city7():
    result = utils.get_city(55.7879, 49.1233)
    assert type(result) == str
    assert result == 'Казань'

@pytest.mark.asyncio
async def test_get_city8():
    result = utils.get_city(50.402395, 30.532690)
    assert type(result) == str
    assert result == 'Киев'

@pytest.mark.asyncio
async def test_get_city9():
    result = utils.get_city(64.539304, 40.518735)
    assert type(result) == str
    assert result == 'Архангельск'

@pytest.mark.asyncio
async def test_get_city10():
    result = utils.get_city(58.004785, 56.237654)
    assert type(result) == str
    assert result == 'Пермь'

@pytest.mark.asyncio
async def test_get_city11():
    result = utils.get_city(43.581509, 39.722882)
    assert type(result) == str
    assert result == 'Сочи'

@pytest.mark.asyncio
async def test_get_city12():
    result = utils.get_city(57.153033, 65.534328 )
    assert type(result) == str
    assert result == 'Тюмень'

@pytest.mark.asyncio
async def test_get_city13():
    result = utils.get_city(62.027833, 129.704151)
    assert type(result) == str
    assert result == 'Якутск'

@pytest.mark.asyncio
async def test_get_city14():
    result = utils.get_city(44.616649, 33.52536)
    assert type(result) == str
    assert result == 'Севастополь'

@pytest.mark.asyncio
async def test_get_city15():
    result = utils.get_city(42.984913, 47.504646)
    assert type(result) == str
    assert result == 'Махачкала'

@pytest.mark.asyncio
async def test_get_country1():
    result = utils.get_country(57.6261, 39.8845)
    assert type(result) == str
    assert result == 'Россия'


@pytest.mark.asyncio
async def test_get_country2():
    result = utils.get_country(57.7677, 40.9263)
    assert type(result) == str
    assert result == 'Россия'

@pytest.mark.asyncio
async def test_get_country3():
    result = utils.get_country(57.0051, 40.9766)
    assert type(result) == str
    assert result == 'Россия'

@pytest.mark.asyncio
async def test_get_country4():
    result = utils.get_country(48.8566, 2.3522)
    assert type(result) == str
    assert result == 'Франция'

@pytest.mark.asyncio
async def test_get_country5():
    result = utils.get_country(40.730610, -73.935242)
    assert type(result) == str
    assert result.lower() == 'соединённые штаты америки'

@pytest.mark.asyncio
async def test_get_country6():
    result = utils.get_country(56.3269, 44.0059)
    assert type(result) == str
    assert result == 'Россия'

@pytest.mark.asyncio
async def test_get_country7():
    result = utils.get_country(55.7879, 49.1233)
    assert type(result) == str
    assert result == 'Россия'
@pytest.mark.asyncio
async def test_generate_osm_image1():
    nodes = [(55.7879, 49.1233), (56.3269, 44.0059)]
    map = await utils.generate_osm_image(nodes)
    assert type(map) == bytes
@pytest.mark.asyncio
async def test_generate_osm_image2():
    nodes = [(55.7879, 49.1233), (40.730610, -73.935242)]
    map = await utils.generate_osm_image(nodes)
    assert type(map) == bytes
@pytest.mark.asyncio
async def test_generate_osm_image3():
    nodes = [(55.7879, 49.1233), (40.730610, -73.935242), (48.8566, 2.3522)]
    map = await utils.generate_osm_image(nodes)
    assert type(map) == bytes

@pytest.mark.asyncio
async def test_generate_osm_image4():
    nodes = [(55.7879, 49.1233), (40.730610, -73.935242), (48.8566, 2.3522), (57.7677, 40.9263), (48.8566, 2.3522), (40.730610, -73.935242), (55.7879, 49.1233)]
    map = await utils.generate_osm_image(nodes)
    assert type(map) == bytes

@pytest.mark.asyncio
async def test_hotels():
    node = (55.7879, 49.1233)
    hotels = await utils.find_hotels(node)
    assert type(hotels) == list
@pytest.mark.asyncio
async def test_cafes():
    node = (55.7879, 49.1233)
    cafes = await utils.find_cafes(node)
    assert type(cafes) == list
@pytest.mark.asyncio
async def test_weather():
    node = (55.7879, 49.1233)
    weather = await utils.get_weather(node)
    assert type(weather) == str
    assert 'Температура' in weather
    assert 'Ощущается как' in weather
    assert 'Влажность' in weather
    assert 'Ветер' in weather
    assert 'Облачность' in weather

@pytest.mark.asyncio
async def test_weather1():
    node = (56.3269, 44.0059)
    weather = await utils.get_weather(node)
    assert type(weather) == str
    assert 'Температура' in weather
    assert 'Ощущается как' in weather
    assert 'Влажность' in weather
    assert 'Ветер' in weather
    assert 'Облачность' in weather
@pytest.mark.asyncio
async def test_weather2():
    node = (48.8566, 2.3522)
    weather = await utils.get_weather(node)
    assert type(weather) == str
    assert 'Температура' in weather
    assert 'Ощущается как' in weather
    assert 'Влажность' in weather
    assert 'Ветер' in weather
    assert 'Облачность' in weather
@pytest.mark.asyncio
async def test_weather3():
    node = (40.730610, -73.935242)
    weather = await utils.get_weather(node)
    assert type(weather) == str
    assert 'Температура' in weather
    assert 'Ощущается как' in weather
    assert 'Влажность' in weather
    assert 'Ветер' in weather
    assert 'Облачность' in weather
@pytest.mark.asyncio
async def test_weather4():
    node = (57.7677, 40.9263)
    weather = await utils.get_weather(node)
    assert type(weather) == str
    assert 'Температура' in weather
    assert 'Ощущается как' in weather
    assert 'Влажность' in weather
    assert 'Ветер' in weather
    assert 'Облачность' in weather
@pytest.mark.asyncio
async def test_weather5():
    node = (57.6261, 39.8845)
    weather = await utils.get_weather(node)
    assert type(weather) == str
    assert 'Температура' in weather
    assert 'Ощущается как' in weather
    assert 'Влажность' in weather
    assert 'Ветер' in weather
    assert 'Облачность' in weather
@pytest.mark.asyncio
async def test_weather6():
    node = (55.359594, 86.0877810)
    weather = await utils.get_weather(node)
    assert type(weather) == str
    assert 'Температура' in weather
    assert 'Ощущается как' in weather
    assert 'Влажность' in weather
    assert 'Ветер' in weather
    assert 'Облачность' in weather
@pytest.mark.asyncio
async def test_weather7():
    node = (54.507014, 36.252277)
    weather = await utils.get_weather(node)
    assert type(weather) == str
    assert 'Температура' in weather
    assert 'Ощущается как' in weather
    assert 'Влажность' in weather
    assert 'Ветер' in weather
    assert 'Облачность' in weather
@pytest.mark.asyncio
async def test_weather8():
    node = (50.402395, 30.532690)
    weather = await utils.get_weather(node)
    assert type(weather) == str
    assert 'Температура' in weather
    assert 'Ощущается как' in weather
    assert 'Влажность' in weather
    assert 'Ветер' in weather
    assert 'Облачность' in weather
@pytest.mark.asyncio
async def test_weather9():
    node = (55.916229, 37.854467)
    weather = await utils.get_weather(node)
    assert type(weather) == str
    assert 'Температура' in weather
    assert 'Ощущается как' in weather
    assert 'Влажность' in weather
    assert 'Ветер' in weather
    assert 'Облачность' in weather
@pytest.mark.asyncio
async def test_not_under_call(storage, bot):
    callback = AsyncMock()
    state = FSMContext(
        storage=storage,
        key=StorageKey(
            bot_id=bot.id,
            chat_id=TEST_CHAT.id,
            user_id=TEST_USER.id
        )
    )
    await not_understand.not_under_call(callback)
    callback.answer.assert_called()
    callback.message.answer.assert_called_with('Ой, что-то пошло не так, нажми сюда -> /main_menu')


@pytest.mark.asyncio
async def test_not_under2(storage, bot):
    message = AsyncMock()
    state = FSMContext(
        storage=storage,
        key=StorageKey(
            bot_id=bot.id,
            chat_id=TEST_CHAT.id,
            user_id=TEST_USER.id
        )
    )
    await not_understand.not_under_mes(message)
    message.answer.assert_called_with('Ты ввёл что-то не то. Попробуй снова. Если ты хочешь вернуться в главное меню нажми /main_menu')

@pytest.mark.asyncio
async def test_cancel(storage, bot):
    message = AsyncMock()
    state = FSMContext(
        storage=storage,
        key=StorageKey(
            bot_id=bot.id,
            chat_id=TEST_CHAT.id,
            user_id=TEST_USER.id
        )
    )
    await cancel.cancel_handler(message, state)
    message.answer.assert_called_with('Отменено',  reply_markup=ReplyKeyboardRemove())
    assert await state.get_state() is None
@pytest.mark.asyncio
async def test_database_conn(storage, bot):
    base.engine = create_engine("postgresql://localhost/postgres?user=postgres&password=secret", echo=True)
    assert type(base.engine) == Engine

@pytest.mark.asyncio
async def test_database_create_user(storage, bot):
    base.engine = create_engine("postgresql://localhost/postgres?user=postgres&password=secret", echo=True)
    with Session(base.engine) as session:
        new_user = users.User(
            first_name='Test user fn',
            last_name='Test user ln',
            bio='Test user bio',
            country='Russia',
            city='Yaroslavl',
            lat=57.6261,
            long=39.8845,
            age=41,
            looking_for_a_partner=True,
            is_male=True,
            telegram_id=int(TEST_USER.id)
        )
        session.add(new_user)
        session.commit()
    with Session(base.engine) as session:
        new_user, = session.query(users.User.telegram_id).filter_by(telegram_id=int(TEST_USER.id)).first()
        assert new_user == int(TEST_USER.id)

@pytest.mark.asyncio
async def test_database_delete_user(storage, bot):
    base.engine = create_engine("postgresql://localhost/postgres?user=postgres&password=secret", echo=True)
    with Session(base.engine) as session:
        new_user = session.query(users.User).filter_by(telegram_id=int(TEST_USER.id)).first()
        session.delete(new_user)
        session.commit()
    with Session(base.engine) as session:
        new_user = session.query(users.User.telegram_id).filter_by(telegram_id=int(TEST_USER.id)).first()
        assert new_user is None

@pytest.mark.asyncio
async def test_database_create_travel(storage, bot):
    base.engine = create_engine("postgresql://localhost/postgres?user=postgres&password=secret", echo=True)
    with Session(base.engine) as session:
        new_user = session.query(users.User.telegram_id).filter_by(telegram_id=int(TEST_USER.id)).first()
        if new_user is not None:
            new_user = session.query(users.User).filter_by(telegram_id=int(TEST_USER.id)).first()
            session.delete(new_user)
            session.commit()
    with Session(base.engine) as session:
        new_user = users.User(
            first_name='Test user fn',
            last_name='Test user ln',
            bio='Test user bio',
            country='Russia',
            city='Yaroslavl',
            lat=57.6261,
            long=39.8845,
            age=41,
            looking_for_a_partner=True,
            is_male=True,
            telegram_id=int(TEST_USER.id)
        )
        session.add(new_user)
        session.commit()
    with Session(base.engine) as session:
        new_user, = session.query(users.User.telegram_id).filter_by(telegram_id=int(TEST_USER.id)).first()
        assert new_user == int(TEST_USER.id)
    with Session(base.engine) as session:
        travel = travels.Travel(
            title='Test travel',
            description='Description test',
            user_id=int(TEST_USER.id),
            is_archived=False
        )
        session.add(travel)
        session.commit()
    with Session(base.engine) as session:
        travel, = session.query(travels.Travel.title).filter_by(user_id=int(TEST_USER.id)).first()
        assert travel == 'Test travel'

@pytest.mark.asyncio
async def test_database_delete_travel(storage, bot):
    base.engine = create_engine("postgresql://localhost/postgres?user=postgres&password=secret", echo=True)
    with Session(base.engine) as session:
        travel = session.query(travels.Travel).filter_by(user_id=int(TEST_USER.id)).first()
        assert travel.title == 'Test travel'
        session.delete(travel)
        session.commit()
    with Session(base.engine) as session:
        travel = session.query(travels.Travel.title).filter_by(user_id=int(TEST_USER.id)).first()
        assert travel is None
    base.engine = create_engine("postgresql://localhost/postgres?user=postgres&password=secret", echo=True)
    with Session(base.engine) as session:
        new_user = session.query(users.User).filter_by(telegram_id=int(TEST_USER.id)).first()
        session.delete(new_user)
        session.commit()
    with Session(base.engine) as session:
        new_user = session.query(users.User.telegram_id).filter_by(telegram_id=int(TEST_USER.id)).first()
        assert new_user is None

@pytest.mark.asyncio
async def test_database_create_location(storage, bot):
    base.engine = create_engine("postgresql://localhost/postgres?user=postgres&password=secret", echo=True)
    with Session(base.engine) as session:
        new_user = session.query(users.User.telegram_id).filter_by(telegram_id=int(TEST_USER.id)).first()
        if new_user is not None:
            new_user = session.query(users.User).filter_by(telegram_id=int(TEST_USER.id)).first()
            session.delete(new_user)
            session.commit()
    with Session(base.engine) as session:
        new_user = users.User(
            first_name='Test user fn',
            last_name='Test user ln',
            bio='Test user bio',
            country='Russia',
            city='Yaroslavl',
            lat=57.6261,
            long=39.8845,
            age=41,
            looking_for_a_partner=True,
            is_male=True,
            telegram_id=int(TEST_USER.id)
        )
        session.add(new_user)
        session.commit()
    with Session(base.engine) as session:
        new_user, = session.query(users.User.telegram_id).filter_by(telegram_id=int(TEST_USER.id)).first()
        assert new_user == int(TEST_USER.id)
    with Session(base.engine) as session:
        travel = travels.Travel(
            title='Test travel',
            description='Description test',
            user_id=int(TEST_USER.id),
            is_archived=False
        )
        session.add(travel)
        session.commit()
    with Session(base.engine) as session:
        travel = session.query(travels.Travel).filter_by(user_id=int(TEST_USER.id)).first()
        assert travel.title == 'Test travel'
        location = travels.Location(
            country='Russia',
            city ='Moscow',
            lat = 55.7558,
            long = 37.6173,
            date_start = datetime.datetime.today(),
            date_end = (datetime.datetime.today()+datetime.timedelta(days=1)),
            travel_id = travel.id
        )
        session.add(location)
        session.commit()
        loc = session.query(travels.Location).filter_by(travel_id=travel.id).first()
        assert loc.city == 'Moscow'
        assert loc.country == 'Russia'
        assert loc.lat == 55.7558
        assert loc.long == 37.6173

@pytest.mark.asyncio
async def test_database_delete_location(storage, bot):
    base.engine = create_engine("postgresql://localhost/postgres?user=postgres&password=secret", echo=True)
    with Session(base.engine) as session:
        travel = session.query(travels.Travel).filter_by(user_id=int(TEST_USER.id)).first()
        loc = session.query(travels.Location).filter_by(travel_id = travel.id).first()
        assert loc.city == 'Moscow'
        assert loc.country == 'Russia'
        assert loc.lat == 55.7558
        assert loc.long == 37.6173
        session.delete(loc)
        session.commit()
        travel = session.query(travels.Travel).filter_by(user_id=int(TEST_USER.id)).first()
        assert travel.title == 'Test travel'
        session.delete(travel)
        session.commit()
    with Session(base.engine) as session:
        travel = session.query(travels.Travel.title).filter_by(user_id=int(TEST_USER.id)).first()
        assert travel is None
    base.engine = create_engine("postgresql://localhost/postgres?user=postgres&password=secret", echo=True)
    with Session(base.engine) as session:
        new_user = session.query(users.User).filter_by(telegram_id=int(TEST_USER.id)).first()
        session.delete(new_user)
        session.commit()
    with Session(base.engine) as session:
        new_user = session.query(users.User.telegram_id).filter_by(telegram_id=int(TEST_USER.id)).first()
        assert new_user is None