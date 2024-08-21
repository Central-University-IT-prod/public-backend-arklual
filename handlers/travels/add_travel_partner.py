from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from handlers.travels.fsm import AddTravelPartner
from keyboards import get_user
from models import base
from models.travels import TravelPartner
from utils import check_user_exist

router = Router()


@router.callback_query(F.data.startswith('add_travel_partner_'))
async def add_travel_partner(callback: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    await callback.answer()
    travel_id = int(callback.data.replace("add_travel_partner_", ''))
    await state.set_state(AddTravelPartner.partner)
    await state.update_data(travel_id=int(travel_id))
    builder.row(InlineKeyboardButton(text='Назад',
                                     callback_data=f'view_travel_{travel_id}'))
    await callback.message.answer('Отправь контакт спутника',
                                  reply_markup=get_user.get(travel_id))
    await callback.message.answer('(контактом в тг или по кнопке внизу экрана)',
                                  reply_markup=builder.as_markup())


@router.message(AddTravelPartner.partner, F.contact)
async def add_travel_partner_contact(message: Message, state: FSMContext):
    partner_id = int(message.contact.user_id)
    data = await state.get_data()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Назад',
                                     callback_data=f'view_travel_{int(data["travel_id"])}'))
    await state.clear()
    with Session(base.engine) as session:
        ids = session.query(TravelPartner.user_id).filter_by(travel_id=int(data['travel_id'])).all()
        for travel_partner_id, in ids:
            if int(partner_id) == int(travel_partner_id):
                await message.answer('Ты уже добавил этого человека в спутники',
                                     reply_markup=builder.as_markup())
                return
    try:
        if check_user_exist(partner_id):
            await message.bot.send_message(partner_id, 'Тебя добавили в путешествие')
        else:
            raise Exception()
    except :
        await message.answer(
            'Отправленный контакт не является моим пользователем(\nПригласи его в меня и попроуй снова',
            reply_markup=builder.as_markup())
        return
    with Session(base.engine) as session:
        ids = session.query(TravelPartner.user_id).filter_by(travel_id=int(data['travel_id'])).all()
        for travel_partner_id, in ids:
            await message.bot.send_message(travel_partner_id,
                                           f'В путешествие {data["travel_id"]} добавлен новый спутник')
        partner = TravelPartner(
            user_id=partner_id,
            travel_id=int(data['travel_id'])
        )
        session.add(partner)
        session.commit()
    await message.answer('Готово!', reply_markup=builder.as_markup())


@router.message(AddTravelPartner.partner, F.user_shared)
async def add_travel_partner_user_shared(message: Message, state: FSMContext):
    partner_id = message.user_shared.user_id
    data = await state.get_data()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Назад',
                                     callback_data=f'view_travel_{int(data["travel_id"])}'))
    await state.clear()
    with Session(base.engine) as session:
        ids = session.query(TravelPartner.user_id).filter_by(travel_id=int(data['travel_id'])).all()
        for travel_partner_id, in ids:
            if int(partner_id) == int(travel_partner_id):
                await message.answer('Ты уже добавил этого человека в спутники',
                                     reply_markup=builder.as_markup())
                return
    try:
        partner_id = (await message.bot.get_chat(partner_id)).id
        if check_user_exist(partner_id):
            await message.bot.send_message(partner_id, 'Тебя добавили в путешествие')
        else:
            raise Exception()
    except:
        await message.answer(
            'Отправленный контакт не является моим пользователем(\nПригласи его в меня и попроуй снова',
            reply_markup=builder.as_markup())
        return
    with Session(base.engine) as session:
        ids = session.query(TravelPartner.user_id)\
            .filter_by(travel_id=int(data['travel_id'])).all()
        for travel_partner_id, in ids:
            await message.bot.send_message(travel_partner_id,
                                           f'В путешествие {data["travel_id"]} \добавлен новый спутник')
        partner = TravelPartner(
            user_id=partner_id,
            travel_id=int(data['travel_id'])
        )
        session.add(partner)
        session.commit()
    await message.answer('Готово!', reply_markup=builder.as_markup())
