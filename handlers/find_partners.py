from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from filters.user_filter import RegisteredCallback
from handlers import main_menu
from models import base, users

router = Router()


@router.callback_query(F.data.startswith('find_new_partners_'), RegisteredCallback())
async def find_new_partners(callback: CallbackQuery):
    page = int(callback.data.replace('find_new_partners_', ''))
    await callback.answer()
    with Session(base.engine) as session:
        me = session.query(users.User).filter_by(telegram_id=int(callback.from_user.id)).first()
        me.looking_for_a_partner = True
        session.commit()
        user_data_text = ''''''
        my_interests = session.query(users.Interest.title)\
            .filter_by(user_id=int(callback.from_user.id)).all()
        pagination_row = []
        all_users = session.query(users.User).all()
        user_found = False
        count_found = 0
        builder = InlineKeyboardBuilder()
        for user in all_users:
            if user.id == me.id:
                continue
            if abs(user.age - me.age) > 5:
                continue
            if not user.looking_for_a_partner:
                continue
            his_interests = session.query(users.Interest.title)\
                .filter_by(user_id=int(user.telegram_id)).all()
            he_match = False
            for my_interest in my_interests:
                if my_interest in his_interests:
                    he_match = True
                    count_found += 1
                    break
            if he_match and count_found == page:
                pagination_row.append(InlineKeyboardButton(text='<-',
                                                           callback_data=f'find_new_partners_{page - 1}'))
            if he_match and count_found == page + 1:
                builder.row(InlineKeyboardButton(text='Связаться', url=f'tg://user?id={user.telegram_id}'))
                user_found = True
                interests_text = ''
                for n, (i,) in enumerate(his_interests):
                    interests_text += str(i).lower()
                    if n + 1 != len(his_interests):
                        interests_text += ', '
                user_data_text = f'''
Имя: {user.first_name}
Фамилия: {user.last_name}
Возраст: {user.age}
Страна: {user.country}
Город: {user.city}
Пол: {'Мужской' if user.is_male else 'Женский'}
Bio:
{user.bio}
-----
Интересы: {interests_text}'''
            if user_found and he_match and count_found == page + 2:
                pagination_row.append(InlineKeyboardButton(text='->',
                                                           callback_data=f'find_new_partners_{page + 1}'))
        if not user_found:
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text='Назад', callback_data='main_menu'))
            await callback.message.answer('К сожалению, люди с похожими интересами не найдены',
                                          reply_markup=builder.as_markup())
        else:
            if pagination_row:
                builder.row(*pagination_row)
            builder.row(InlineKeyboardButton(text='Больше не ищу спутника', callback_data='stop_search_partners'))
            builder.row(InlineKeyboardButton(text='Назад', callback_data='main_menu'))
            await callback.message.edit_text(user_data_text, reply_markup=builder.as_markup())


@router.callback_query(F.data == 'stop_search_partners', RegisteredCallback())
async def stop_search_partners(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    with Session(base.engine) as session:
        user = session.query(users.User).filter_by(telegram_id=int(callback.from_user.id)).first()
        user.looking_for_a_partner = False
        session.commit()
    await callback.message.answer('Теперь тебя никто не сможет пригласить в поездку')
    await main_menu.command_main_menu_handler(callback.message, state)
