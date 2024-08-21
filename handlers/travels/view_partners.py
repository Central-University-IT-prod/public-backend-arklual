from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from models import base
from models.travels import TravelPartner, Travel
from models.users import User

router = Router()


@router.callback_query(F.data.startswith("view_trav_partners_"))
async def view_travel_partners(callback: CallbackQuery):
    travel_id = callback.data.replace('view_trav_partners_', '')
    await callback.answer()
    builder = InlineKeyboardBuilder()
    with Session(base.engine) as session:
        tmp_partners = session.query(TravelPartner).filter_by(travel_id=int(travel_id)).all()
        author, = session.query(Travel.user_id).filter_by(id=int(travel_id)).first()
        partners = []
        for partner in tmp_partners:
            partners.append(int(partner.user_id))
        if author not in partners:
            partners.append(author)
        if callback.from_user.id in partners:
            partners.remove(callback.from_user.id)
        if callback:
            if callback.from_user.id in partners:
                partners.remove(callback.from_user.id)
        answer_text = 'Твои спутники:'
        for n, i in enumerate(partners):
            user = session.query(User).filter_by(telegram_id=i).first()
            answer_text += f'\n{n + 1}. {user.first_name} {user.last_name}'
        if len(partners) == 0:
            answer_text = 'У тебя пока нет спутников, но ты можешь добавить знакомых или найти новых друзей по интересам'
            builder.row(InlineKeyboardButton(text='Добавить спутника', callback_data=f'add_travel_partner_{travel_id}'))
            builder.row(InlineKeyboardButton(text='Найти спутника', callback_data='find_new_partners_0'))
        if int(author) == int(callback.from_user.id) and len(partners) != 0:
            builder.row(InlineKeyboardButton(text='Удалить спутника', callback_data='del_trav_partner_{travel_id}'))
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        await callback.message.answer(answer_text, reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("del_trav_partner_"))
async def del_trav_partner(callback: CallbackQuery):
    travel_id = callback.data.replace('del_trav_partner_', '')
    await callback.answer()
    builder = InlineKeyboardBuilder()
    with Session(base.engine) as session:
        tmp_partners = session.query(TravelPartner).filter_by(travel_id=int(travel_id)).all()
        author, = session.query(Travel.user_id).filter_by(id=int(travel_id)).first()
        partners = []
        for partner in tmp_partners:
            partners.append(int(partner.user_id))
        if author not in partners:
            partners.append(author)
        if callback.from_user.id in partners:
            partners.remove(callback.from_user.id)
        if callback:
            if callback.from_user.id in partners:
                partners.remove(callback.from_user.id)
        for i in partners:
            user = session.query(User).filter_by(telegram_id=i).first()
            builder.row(InlineKeyboardButton(text=f'{user.first_name} {user.last_name}',
                                             callback_data=f'del_partn_chosen_{user.telegram_id}_{travel_id}'))
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        await callback.message.answer('Выбери, которого спутника ты хочешь удалить:', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("del_partn_chosen_"))
async def del_partn_chosen(callback: CallbackQuery):
    user_id, travel_id = callback.data.replace('del_partn_chosen_', '').split('_')
    await callback.answer()
    builder = InlineKeyboardBuilder()
    with Session(base.engine) as session:
        partner = session.query(TravelPartner).filter_by(travel_id=int(travel_id), user_id=int(user_id)).first()
        session.delete(partner)
        session.commit()
        ids = session.query(TravelPartner.user_id).filter_by(travel_id=int(travel_id)).all()
        try:
            await callback.bot.send_message(int(user_id), f'Тебя удалили из путешествия {travel_id}')
        except:
            pass
        for user_id, in ids:
            try:
                await callback.bot.send_message(user_id, f'В путешествие {travel_id} удалён спутник')
            except:
                pass
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
    await callback.message.answer('Успешно удалено', reply_markup=builder.as_markup())
