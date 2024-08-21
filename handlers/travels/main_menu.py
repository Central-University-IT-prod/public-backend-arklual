from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from filters.user_filter import RegisteredCallback
from handlers.travels import add_travel_partner, alter, attractions_suggest, create_travel, maps, \
    delete_travel, notes, packhelp, splitwise, travel_menu, weather, cafes, hotels, view_partners
from models import base
from models.travels import Travel, TravelPartner

router = Router()
router.include_routers(add_travel_partner.router, alter.router, attractions_suggest.router, create_travel.router,
                       maps.router, \
                       delete_travel.router, notes.router, packhelp.router, splitwise.router, travel_menu.router,
                       weather.router, cafes.router, \
                       hotels.router, view_partners.router)


@router.callback_query(F.data.startswith("my_travels_"), RegisteredCallback())
async def my_travels(callback: CallbackQuery):
    await callback.answer()
    last_id = (await callback.message.edit_text('Загружаю...')).message_id
    with Session(base.engine) as session:
        travels = session. \
            query(Travel.title, Travel.id, Travel.is_archived). \
            filter_by(user_id=int(callback.from_user.id)).all()
        travels1_ids = session.query(TravelPartner.travel_id).filter_by(user_id=int(callback.from_user.id)).all()
        travels1 = []
        for t_id, in travels1_ids:
            travel = session. \
                query(Travel.title, Travel.id, Travel.is_archived). \
                filter_by(id=int(t_id)).first()
            title, travel_id, is_archived = travel
            travels1.append(travel)
    travels += travels1
    builder = InlineKeyboardBuilder()
    counter_0 = int(callback.data.replace("my_travels_", ''))
    cnt = 0
    counter = counter_0
    while cnt != 5:
        if len(travels) == counter:
            break
        title, travel_id, is_archived = travels[counter]
        if not is_archived:
            builder.row(InlineKeyboardButton(
                text=f"{title}",
                callback_data=f"view_travel_{travel_id}")
            )
            cnt += 1
        counter += 1
    cnt = 0
    for title, travel_id, is_archived in travels:
        if is_archived:
            continue
        cnt += 1
    pagination_row = []
    if counter_0 > 0:
        pagination_row.append(InlineKeyboardButton(
            text="<--",
            callback_data=f"my_travels_{counter_0 - 5}")
        )
    if cnt - counter_0 >= 6:
        pagination_row.append(InlineKeyboardButton(
            text="-->",
            callback_data=f"my_travels_{counter_0 + 5}")
        )
    if pagination_row != []:
        builder.row(*pagination_row)
    builder.row(InlineKeyboardButton(
        text="Добавить путешествие",
        callback_data="create_travel")
    )
    builder.row(InlineKeyboardButton(
        text="В главное меню",
        callback_data="main_menu")
    )
    await callback.message.edit_text('Твои путешествия:', reply_markup=builder.as_markup())
    attemp = 0
    for i in range(last_id - 1, -1, -1):
        if attemp == 3:
            break
        try:
            await callback.bot.delete_message(callback.from_user.id, i)
        except:
            attemp += 1


@router.callback_query(F.data.startswith("my_archive_travels_"), RegisteredCallback())
async def my_archive_travels(callback: CallbackQuery):
    await callback.answer()
    last_id = (await callback.message.edit_text('Загружаю...')).message_id
    with Session(base.engine) as session:
        travels = session. \
            query(Travel.title, Travel.id, Travel.is_archived). \
            filter_by(user_id=int(callback.from_user.id)).all()
        travels1_ids = session.query(TravelPartner.travel_id).filter_by(user_id=int(callback.from_user.id)).all()
        travels1 = []
        for t_id, in travels1_ids:
            travel = session. \
                query(Travel.title, Travel.id, Travel.is_archived). \
                filter_by(id=int(t_id)).first()
            title, travel_id, is_archived = travel
            travels1.append(travel)
    travels += travels1
    builder = InlineKeyboardBuilder()
    counter_0 = int(callback.data.replace("my_archive_travels_", ''))
    cnt = 0
    counter = counter_0
    while cnt != 5:
        if len(travels) == counter:
            break
        title, travel_id, is_archived = travels[counter]
        if is_archived:
            builder.row(InlineKeyboardButton(
                text=f"{title}",
                callback_data=f"view_travel_{travel_id}")
            )
            cnt += 1
        counter += 1
    cnt = 0
    for title, travel_id, is_archived in travels:
        if not is_archived:
            continue
        cnt += 1
    pagination_row = []
    if counter_0 > 0:
        pagination_row.append(InlineKeyboardButton(
            text="<--",
            callback_data=f"my_archive_travels_{counter_0 - 5}")
        )
    if cnt - counter_0 >= 6:
        pagination_row.append(InlineKeyboardButton(
            text="-->",
            callback_data=f"my_archive_travels_{counter_0 + 5}")
        )
    if pagination_row != []:
        builder.row(*pagination_row)
    builder.row(InlineKeyboardButton(
        text="В главное меню",
        callback_data="main_menu")
    )
    await callback.message.edit_text('Твои путешествия в архиве:', reply_markup=builder.as_markup())
    attemp = 0
    for i in range(last_id - 1, -1, -1):
        if attemp == 3:
            break
        try:
            await callback.bot.delete_message(callback.from_user.id, i)
        except:
            attemp += 1
