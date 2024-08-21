from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
import strings
from filters.user_filter import Registered, RegisteredCallback
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class FeedbackForm(StatesGroup):
    feedback = State()

@router.message(Command('main_menu'), Registered())
async def command_main_menu_handler(message: Message, state:FSMContext):
    await state.clear()
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="💼 Мой профиль",
        callback_data="profile")
    )
    builder.row(types.InlineKeyboardButton(
        text="✈️ Мои путешествия",
        callback_data="my_travels_0")
    )
    builder.row(types.InlineKeyboardButton(
        text="⌛️ Архив путешествий",
        callback_data="my_archive_travels_0")
    )
    builder.row(types.InlineKeyboardButton(
        text="👨‍🦱 Найти спутников",
        callback_data="find_new_partners_0")
    )
    builder.row(types.InlineKeyboardButton(
        text="☎️ Обратная связь",
        callback_data="feedback")
    )
    await message.answer('Koltso Travel Bot', reply_markup=ReplyKeyboardRemove())
    await message.answer(strings.MAIN_MENU, reply_markup=builder.as_markup())


@router.callback_query(F.data == 'main_menu', RegisteredCallback())
async def command_main_menu_callback(callback: CallbackQuery, state:FSMContext):
    await state.clear()
    await callback.answer()
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="💼 Мой профиль",
        callback_data="profile")
    )
    builder.row(types.InlineKeyboardButton(
        text="✈️ Мои путешествия",
        callback_data="my_travels_0")
    )
    builder.row(types.InlineKeyboardButton(
        text="⌛️ Архив путешествий",
        callback_data="my_archive_travels_0")
    )
    builder.row(types.InlineKeyboardButton(
        text="👨‍🦱 Найти спутников",
        callback_data="find_new_partners_0")
    )
    builder.row(types.InlineKeyboardButton(
        text="☎️ Обратная связь",
        callback_data="feedback")
    )
    await callback.message.answer('Koltso Travel Bot', reply_markup=ReplyKeyboardRemove())
    last_id = (await callback.message.answer(strings.MAIN_MENU, reply_markup=builder.as_markup())).message_id
    attemp = 0
    for i in range(last_id-1, -1, -1):
        if attemp == 3:
            break
        try:
            await callback.bot.delete_message(callback.from_user.id, i)
        except:
            attemp += 1

@router.callback_query(F.data == 'feedback')
async def feedback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    await callback.message.answer('Напиши, что хочешь передать моему разработчику')
    await state.set_state(FeedbackForm.feedback)
    
@router.message(FeedbackForm.feedback)
async def feedback_entered(message: Message, state:FSMContext):
    await state.clear()
    await message.answer('Спасибо! Отправил твои слова разработчику')
    try: await message.bot.send_message(685823428, message.text)
    except: pass
    await command_main_menu_handler(message, state)