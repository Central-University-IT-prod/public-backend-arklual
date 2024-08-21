from datetime import date

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from handlers.travels.fsm import CreateNote, SplitBuy
from models import base
from models.travels import Travel, TravelPartner, TravelNote, Debt
from models.users import User

router = Router()


@router.callback_query(F.data.startswith("splitwise_"))
async def splitwise(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer('Загрузка...', reply_markup=ReplyKeyboardRemove())
    travel_id = callback.data.replace('splitwise_', '')
    with Session(base.engine) as session:
        debts_borrowed = session.query(Debt).filter_by(debtor_id=int(callback.from_user.id),
                                                       travel_id=int(travel_id)).all()
        debts_given = session.query(Debt).filter_by(creditor_id=int(callback.from_user.id),
                                                    travel_id=int(travel_id)).all()
        sum_borrowed = 0
        sum_given = 0
        for debt in debts_borrowed:
            sum_borrowed += debt.money
        for debt in debts_given:
            sum_given += debt.money
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Купить в сплит', callback_data=f'give_debt_{travel_id}'))
    borrowed = False
    if sum_borrowed > 0:
        borrowed = True
    if borrowed:
        builder.row(InlineKeyboardButton(text='Отдать долг', callback_data=f'give_back_debt_{travel_id}'))
    builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
    await callback.message.answer(f'Твой долг: {sum_borrowed}₽\nТебе должны: {sum_given}₽',
                                  reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("give_back_debt_"))
async def give_back_debt(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    builder = InlineKeyboardBuilder()
    travel_id = callback.data.replace('give_back_debt_', '')
    with Session(base.engine) as session:
        debts_borrowed = session.query(Debt).filter_by(debtor_id=int(callback.from_user.id),
                                                       travel_id=int(travel_id)).all()
        to_give_back = {}
        for debt in debts_borrowed:
            if debt.creditor_id not in to_give_back.keys():
                to_give_back[debt.creditor_id] = 0
            to_give_back[debt.creditor_id] += debt.money
        ask_text = 'Выбери, кому ты хочешь вернуть долг. Ты должен:\n'
        for i, j in to_give_back.items():
            user = session.query(User).filter_by(telegram_id=i).first()
            ask_text += f'\n{user.first_name} {user.last_name}: {j}₽'
            builder.row(InlineKeyboardButton(text=f'{user.first_name} {user.last_name}',
                                             callback_data=f'give_back_user_debt_{user.telegram_id}'))
        await state.set_state(SplitBuy.user)
        await state.update_data(travel_id=int(travel_id))
        await callback.message.answer(ask_text, reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("give_back_user_debt_"))
async def give_back_user_debt(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    travel_id = data['travel_id']
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
    creditor_id = callback.data.replace('give_back_user_debt_', '')
    with Session(base.engine) as session:
        debts_borrowed = session.query(Debt).filter_by(debtor_id=int(callback.from_user.id),
                                                       creditor_id=int(creditor_id), travel_id=int(travel_id)).all()
        for debt in debts_borrowed:
            session.delete(debt)
        session.commit()
        await callback.message.answer('Готово', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("give_debt_"))
async def give_debt(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    travel_id = callback.data.replace('give_debt_', '')
    await state.set_state(SplitBuy.money)
    await state.update_data(travel_id=int(travel_id))
    await callback.message.answer('Введи сумму')


@router.message(SplitBuy.money, F.text.regexp(r'^[-+]?[0-9]*[.,]?[0-9]+(?:[eE][-+]?[0-9]+)?$'))
async def give_debt_money(message: Message, state: FSMContext):
    await state.update_data(money_left=float(message.text.replace(',', '.')))
    await state.set_state(SplitBuy.user)
    await choose_user_for_debt_helper(message, state)


async def choose_user_for_debt_helper(message: Message, state: FSMContext, callback: CallbackQuery = None):
    builder = InlineKeyboardBuilder()
    data = await state.get_data()
    travel_id = int(data['travel_id'])
    with Session(base.engine) as session:
        tmp_partners = session.query(TravelPartner).filter_by(travel_id=int(travel_id)).all()
        author, = session.query(Travel.user_id).filter_by(id=int(travel_id)).first()
        partners = []
        for partner in tmp_partners:
            partners.append(int(partner.user_id))
        if author not in partners:
            partners.append(author)
        if message.from_user.id in partners:
            partners.remove(message.from_user.id)
        if callback:
            if callback.from_user.id in partners:
                partners.remove(callback.from_user.id)
        for i in partners:
            user = session.query(User).filter_by(telegram_id=i).first()
            builder.row(InlineKeyboardButton(text=f'{user.first_name} {user.last_name}',
                                             callback_data=f'give_user_debt_{user.telegram_id}'))
        await message.answer('Выбери участника покупки', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("give_user_debt_"))
async def give_user_debt(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.data.replace('give_user_debt_', '')
    await state.set_state(SplitBuy.money_need)
    await state.update_data(user_id=int(user_id))
    await callback.message.answer('Введи сумму, который должен этот человек')


@router.message(SplitBuy.money_need, F.text.regexp(r'^[-+]?[0-9]*[.,]?[0-9]+(?:[eE][-+]?[0-9]+)?$'))
async def give_debt_money_need(message: Message, state: FSMContext):
    money_need = message.text.strip().replace(',', '.')
    money_need = float(money_need)
    data = await state.get_data()
    travel_id = int(data['travel_id'])
    user_id = int(data['user_id'])
    money_left = float(data['money_left'])
    if money_left - money_need < 0:
        await state.clear()
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        await message.answer('Ой, ты уже ввёл суммы больше, чем вся покупка, начни заполнять форму сначала',
                             reply_markup=builder.as_markup())
        return
    money_left -= money_need
    with Session(base.engine) as session:
        debts = session.query(Debt).filter_by(debtor_id=message.from_user.id, creditor_id=user_id,
                                              travel_id=travel_id).all()
        sum_money = 0
        for i in range(len(debts)):
            sum_money += debts[i].money
        for i in range(len(debts)):
            if money_need == 0:
                break
            if debts[i].money > money_need:
                debts[i].money -= money_need
                money_need = 0
            else:
                money_need -= debts[i].money
                session.delete(debts[i])
        if money_need > 0:
            debt = Debt(
                debtor_id=user_id,
                creditor_id=message.from_user.id,
                travel_id=travel_id,
                money=money_need
            )
            session.add(debt)
        session.commit()
        await state.update_data(money_left=money_left)
    await state.set_state(SplitBuy.user)
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Добавить ещё человека', callback_data=f'add_give_debt_user_{travel_id}'))
    builder.row(InlineKeyboardButton(text='Завершить', callback_data=f'end_give_debt_{travel_id}'))
    await message.answer('Человек добавлен успешно!', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("add_give_debt_user_"))
async def add_give_debt_user(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await choose_user_for_debt_helper(callback.message, state=state, callback=callback)


@router.callback_query(F.data.startswith("end_give_debt_"))
async def end_give_debt(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    money_left = float(data['money_left'])
    travel_id = int(data['travel_id'])
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'),
                InlineKeyboardButton(text='Прикрепить фото чека', callback_data=f'check_split_{travel_id}'))
    await callback.message.answer(f'Готово! Твой чек: {money_left}₽', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("check_split_"))
async def check_split(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    travel_id = callback.data.replace('check_split_', '')
    with Session(base.engine) as session:
        note = TravelNote(
            author_id=int(callback.from_user.id),
            travel_id=int(travel_id),
            is_public=True,
            title=f'Split - {date.today()}'
        )
        session.add(note)
        session.commit()
        travel_id = note.id
        await state.set_state(CreateNote.photo)
        await state.update_data(note_id=travel_id)
        await callback.message.answer('Отправь фото (как фото, а не как файл)')
