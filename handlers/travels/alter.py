from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from filters.travel_filter import TitleExist, TitleNotExist
from handlers.travels.fsm import AlterTitle, AlterDescription
from models import base
from models.travels import Travel

router = Router()


@router.callback_query(F.data.startswith("alter_travel_title_"))
async def alter_travel_title(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    title_id = int(callback.data.replace("alter_travel_title_", ''))
    await state.set_state(AlterTitle.title)
    await state.update_data(travel_id=int(title_id))
    await callback.message.answer('Введи новое название', reply_markup=ReplyKeyboardRemove())


@router.message(AlterTitle.title, F.text, TitleExist())
async def title_invalid1(message: Message, state: FSMContext):
    await message.answer('У тебя уже есть путешествие с таким названием, введи, пожалуйста, другое',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(AlterTitle.title)


@router.message(AlterTitle.title, TitleNotExist(), F.text.len() <= 255)
async def alter_travel_title_entered(message: Message, state: FSMContext):
    travel_id = (await state.get_data())['travel_id']
    await state.clear()
    with Session(base.engine) as session:
        travel = session.query(Travel).filter_by(id=int(travel_id)).first()
        travel.title = message.text
        session.commit()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
    await message.answer('Название успешно изменено!', reply_markup=builder.as_markup())


@router.message(AlterTitle.title)
async def title_invalid2(message: Message, state: FSMContext):
    await message.answer(
        'Ты ввёл что-то не то, попробуй снова. Обращаю внимание, длина названия должна быть не больше 255 символов',
        reply_markup=ReplyKeyboardRemove())
    await state.set_state(AlterTitle.title)


@router.callback_query(F.data.startswith("alter_travel_desc_"))
async def alter_travel_desc(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    travel_id = int(callback.data.replace("alter_travel_desc_", ''))
    await state.set_state(AlterDescription.description)
    await state.update_data(travel_id=int(travel_id))
    await callback.message.answer('Введи новое описание', reply_markup=ReplyKeyboardRemove())


@router.message(AlterDescription.description, F.text)
async def alter_travel_desc_entered(message: Message, state: FSMContext):
    travel_id = (await state.get_data())['travel_id']
    await state.clear()
    with Session(base.engine) as session:
        travel = session.query(Travel).filter_by(id=int(travel_id)).first()
        travel.description = message.text
        session.commit()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
    await message.answer('Описание успешно изменено!', reply_markup=builder.as_markup())
