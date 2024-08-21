from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_media_group import media_group_handler
from sqlalchemy.orm import Session

from handlers.travels.fsm import CreateNote
from models import base
from models.travels import NoteAttachment, TravelNote, Travel

router = Router()


@router.callback_query(F.data.startswith('view_notes_'))
async def view_notes(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer('Загружаю...', reply_markup=ReplyKeyboardRemove())
    travel_id = int(callback.data.replace("view_notes_", '').split('_')[0])
    with Session(base.engine) as session:
        travel = session.query(Travel.id).filter_by(id=travel_id, user_id=int(callback.from_user.id)).first()
        notes = session.query(TravelNote).filter_by(travel_id=travel_id).all()
        builder = InlineKeyboardBuilder()
        counter_0 = int(callback.data.replace("view_notes_", '').split('_')[1])
        counter = counter_0
        cnt = 0
        while cnt < 5:
            if counter == len(notes):
                break
            note = notes[counter]
            counter += 1
            if not note.is_public and travel is None:
                continue
            builder.row(InlineKeyboardButton(
                text=f"{str(note.title).strip().replace('\n', '')}",
                callback_data=f"view_note_{note.id}")
            )
            cnt+=1
        cnt = 0
        for note in notes:
            if not note.is_public and travel is None:
                continue
            cnt += 1
        pagination_row = []
        if counter_0 > 0:
            pagination_row.append(InlineKeyboardButton(
                text="<--",
                callback_data=f"view_notes_{travel_id}_{counter_0 - 5}")
            )
        if cnt - counter_0 >= 6:
            pagination_row.append(InlineKeyboardButton(
                text="-->",
                callback_data=f"view_notes_{travel_id}_{counter_0 + 5}")
            )
        if pagination_row != []:
            builder.row(*pagination_row)
        builder.row(InlineKeyboardButton(text='Добавить публичную заметку', callback_data=f'create_note_{travel_id}_1'))
        builder.row(InlineKeyboardButton(text='Добавить приватную заметку', callback_data=f'create_note_{travel_id}_0'))
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_travel_{travel_id}'))
        await callback.message.answer(f'Заметки к путешествию {travel_id}:', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('create_note_'))
async def create_note(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    travel_id = int(callback.data.replace("create_note_", '').split('_')[0])
    is_public = True if callback.data.replace("create_note_", '').split('_')[1] == '1' else 0
    await state.set_state(CreateNote.title)
    await state.update_data(travel_id=travel_id)
    await state.update_data(is_public=is_public)
    await callback.message.answer('Введи название заметки')


@router.message(CreateNote.title, F.text, F.text.len() <= 255)
async def create_note_title_entered_valid(message: Message, state: FSMContext):
    data = (await state.get_data())
    await state.clear()
    travel_id = data['travel_id']
    is_public = data['is_public']
    with Session(base.engine) as session:
        note = TravelNote(
            author_id=int(message.from_user.id),
            travel_id=travel_id,
            is_public=is_public,
            title=message.text.strip().replace('\n', '')
        )
        session.add(note)
        session.commit()
        note_id = note.id
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Добавить текст', callback_data=f'add_text_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить фото', callback_data=f'add_photo_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить видео', callback_data=f'add_video_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить файл', callback_data=f'add_file_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Готово', callback_data=f'view_notes_{travel_id}_0'))
        await message.answer(message.text, reply_markup=builder.as_markup())


@router.message(CreateNote.title)
async def create_note_title_entered_invalid(message: Message, state: FSMContext):
    await message.answer('Ты ввёл что-то не так, обращаю внимание, название должно быть короче 255 символов')
    await state.set_state(CreateNote.title)


@router.callback_query(F.data.startswith('add_text_note_'))
async def add_text_note(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    note_id = int(callback.data.replace("add_text_note_", ''))
    await state.set_state(CreateNote.text)
    await state.update_data(note_id=note_id)
    await callback.message.answer('Введи текст заметки')


@router.message(CreateNote.text, F.text)
async def add_text_note_creation(message: Message, state: FSMContext):
    data = (await state.get_data())
    await state.clear()
    note_id = data['note_id']
    with Session(base.engine) as session:
        note = session.query(TravelNote).filter_by(id=note_id).first()
        note.text = str(message.text)
        title = str(note.title)
        session.commit()
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Прикрепить фото', callback_data=f'add_photo_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить видео', callback_data=f'add_video_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить файл', callback_data=f'add_file_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Готово', callback_data=f'view_notes_{note.travel_id}_0'))
        await message.answer(f'{title}\n{message.text}', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('add_photo_note_'))
async def note_add_photo(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    note_id = int(callback.data.replace("add_photo_note_", ''))
    await state.set_state(CreateNote.photo)
    await state.update_data(note_id=note_id)
    await callback.message.answer('Отправь фото (как фото, а не как файл)')


@router.callback_query(F.data.startswith('add_video_note_'))
async def note_add_video(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    note_id = int(callback.data.replace("add_video_note_", ''))
    await state.set_state(CreateNote.video)
    await state.update_data(note_id=note_id)
    await callback.message.answer('Отправь видео (как видео, а не как файл)')


@router.callback_query(F.data.startswith('add_file_note_'))
async def note_add_file(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    note_id = int(callback.data.replace("add_file_note_", ''))
    await state.set_state(CreateNote.file)
    await state.update_data(note_id=note_id)
    await callback.message.answer('Отправь файл')


@router.message(F.media_group_id, F.content_type.in_({'photo'}))
@media_group_handler
async def album_handler(messages, state: FSMContext):
    data = (await state.get_data())
    await state.clear()
    note_id = data['note_id']
    await state.update_data(note_id=note_id)
    with Session(base.engine) as session:
        for message in messages:
            attachment = NoteAttachment(
                note_id=note_id,
                photo_telegram_id=message.photo[-1].file_id
            )
            session.add(attachment)
            session.commit()
        note = session.query(TravelNote).filter_by(id=note_id).first()
        note_text = note.text
        title = str(note.title)
        builder = InlineKeyboardBuilder()
        if note_text is None:
            builder.row(InlineKeyboardButton(text='Заменить/добавить текст', callback_data=f'add_text_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить фото', callback_data=f'add_photo_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить видео', callback_data=f'add_video_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить файл', callback_data=f'add_file_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Готово', callback_data=f'view_notes_{note.travel_id}_0'))
        await messages[0].answer(f'{title}\n{note_text if note_text else ""}', reply_markup=builder.as_markup())


@router.message(CreateNote.photo, F.photo)
async def add_photo_note_creation(message: Message, state: FSMContext):
    data = (await state.get_data())
    await state.clear()
    note_id = data['note_id']
    await state.update_data(note_id=note_id)
    with Session(base.engine) as session:
        attachment = NoteAttachment(
            note_id=note_id,
            photo_telegram_id=message.photo[-1].file_id
        )
        session.add(attachment)
        session.commit()
        note = session.query(TravelNote).filter_by(id=note_id).first()
        note_text = note.text
        title = str(note.title)
        builder = InlineKeyboardBuilder()
        if note_text is None:
            builder.row(InlineKeyboardButton(text='Заменить/добавить текст', callback_data=f'add_text_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить фото', callback_data=f'add_photo_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить видео', callback_data=f'add_video_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить файл', callback_data=f'add_file_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Готово', callback_data=f'view_notes_{note.travel_id}_0'))
        await message.answer(f'{title}\n{note_text if note_text else ""}', reply_markup=builder.as_markup())


@router.message(CreateNote.photo)
async def add_photo_note_creation_invalid(message: Message, state: FSMContext):
    await message.answer('Ты отправил что-то не так, попробуй снова')
    await state.set_state(CreateNote.photo)


@router.message(F.media_group_id, F.content_type.in_({'video'}))
@media_group_handler
async def videoalbum_handler(messages, state: FSMContext):
    data = (await state.get_data())
    await state.clear()
    note_id = data['note_id']
    await state.update_data(note_id=note_id)
    with Session(base.engine) as session:
        for message in messages:
            attachment = NoteAttachment(
                note_id=note_id,
                video_telegram_id=message.video.file_id
            )
            session.add(attachment)
            session.commit()
        note = session.query(TravelNote).filter_by(id=note_id).first()
        note_text = note.text
        title = str(note.title)
        builder = InlineKeyboardBuilder()
        if note_text is None:
            builder.row(InlineKeyboardButton(text='Заменить/добавить текст', callback_data=f'add_text_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить фото', callback_data=f'add_photo_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить видео', callback_data=f'add_video_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить файл', callback_data=f'add_file_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Готово', callback_data=f'view_notes_{note.travel_id}_0'))
        await messages[0].answer(f'{title}\n{note_text if note_text else ""}', reply_markup=builder.as_markup())


@router.message(CreateNote.video, F.video)
async def add_video_note_creation(message: Message, state: FSMContext):
    data = (await state.get_data())
    await state.clear()
    note_id = data['note_id']
    with Session(base.engine) as session:
        attachment = NoteAttachment(
            note_id=note_id,
            video_telegram_id=message.video.file_id
        )
        session.add(attachment)
        session.commit()
        note = session.query(TravelNote).filter_by(id=note_id).first()
        note_text = note.text
        title = str(note.title)
        builder = InlineKeyboardBuilder()
        if note_text is None:
            builder.row(InlineKeyboardButton(text='Заменить/добавить текст', callback_data=f'add_text_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить фото', callback_data=f'add_photo_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить видео', callback_data=f'add_video_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить файл', callback_data=f'add_file_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Готово', callback_data=f'view_notes_{note.travel_id}_0'))
        await message.answer(f'{title}\n{note_text if note_text else ""}', reply_markup=builder.as_markup())


@router.message(CreateNote.video)
async def add_video_note_creation_invalid(message: Message, state: FSMContext):
    await message.answer('Ты отправил что-то не так, попробуй снова')
    await state.set_state(CreateNote.video)


@router.message(F.media_group_id, F.content_type.in_({'document'}))
@media_group_handler
async def filealbum_handler(messages, state: FSMContext):
    data = (await state.get_data())
    await state.clear()
    note_id = data['note_id']
    await state.update_data(note_id=note_id)
    with Session(base.engine) as session:
        for message in messages:
            attachment = NoteAttachment(
                note_id=note_id,
                file_telegram_id=message.document.file_id
            )
            session.add(attachment)
            session.commit()
        note = session.query(TravelNote).filter_by(id=note_id).first()
        note_text = note.text
        title = str(note.title)
        builder = InlineKeyboardBuilder()
        if note_text is None:
            builder.row(InlineKeyboardButton(text='Заменить/добавить текст', callback_data=f'add_text_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить фото', callback_data=f'add_photo_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить видео', callback_data=f'add_video_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить файл', callback_data=f'add_file_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Готово', callback_data=f'view_notes_{note.travel_id}_0'))
        await messages[0].answer(f'{title}\n{note_text if note_text else ""}', reply_markup=builder.as_markup())


@router.message(CreateNote.file, F.document)
async def add_file_note_creation(message: Message, state: FSMContext):
    data = (await state.get_data())
    await state.clear()
    note_id = data['note_id']
    with Session(base.engine) as session:
        attachment = NoteAttachment(
            note_id=note_id,
            file_telegram_id=message.document.file_id
        )
        session.add(attachment)
        session.commit()
        note = session.query(TravelNote).filter_by(id=note_id).first()
        note_text = note.text
        title = str(note.title)
        builder = InlineKeyboardBuilder()
        if note_text is None:
            builder.row(InlineKeyboardButton(text='Заменить/добавить текст', callback_data=f'add_text_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить фото', callback_data=f'add_photo_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить видео', callback_data=f'add_video_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить файл', callback_data=f'add_file_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Готово', callback_data=f'view_notes_{note.travel_id}_0'))
        await message.answer(f'{title}\n{note_text if note_text else ""}', reply_markup=builder.as_markup())


@router.message(CreateNote.file)
async def add_file_note_creation_invalid(message: Message, state: FSMContext):
    await message.answer('Ты отправил что-то не так, попробуй снова')
    await state.set_state(CreateNote.file)


@router.callback_query(F.data.startswith('view_note_'))
async def view_note(callback: CallbackQuery):
    await callback.answer()
    note_id = int(callback.data.replace("view_note_", ''))
    with Session(base.engine) as session:
        note = session.query(TravelNote).filter_by(id=note_id).first()
        title = str(note.title)
        note_text = note.text
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Фото', callback_data=f'photos_view_note_{note_id}'),
                    InlineKeyboardButton(text='Видео', callback_data=f'videos_view_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Файлы', callback_data=f'files_view_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Заменить/добавить текст', callback_data=f'add_text_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить фото', callback_data=f'add_photo_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить видео', callback_data=f'add_video_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Прикрепить файл', callback_data=f'add_file_note_{note_id}'))
        builder.row(InlineKeyboardButton(text='Удалить', callback_data=f'are_you_sure_delete_note_{note_id}'),
                    InlineKeyboardButton(text='Назад', callback_data=f'view_notes_{note.travel_id}_0'))
        await callback.message.answer(f'{title}\n{note_text if note_text else ""}', reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith('photos_view_note_'))
async def view_note_photos(callback: CallbackQuery):
    await callback.answer()
    note_id = int(callback.data.replace("photos_view_note_", ''))
    with Session(base.engine) as session:
        attachments = session.query(NoteAttachment).filter_by(note_id=note_id).all()
        sent = False
        for at in attachments:
            if at.photo_telegram_id:
                sent = True
                await callback.message.answer_photo(at.photo_telegram_id)
        if not sent:
            await callback.message.answer('У вас не прикреплено ни одно фото')


@router.callback_query(F.data.startswith('videos_view_note_'))
async def view_note_videos(callback: CallbackQuery):
    await callback.answer()
    note_id = int(callback.data.replace("videos_view_note_", ''))
    with Session(base.engine) as session:
        attachments = session.query(NoteAttachment).filter_by(note_id=note_id).all()
        sent = False
        for at in attachments:
            if at.video_telegram_id:
                sent = True
                await callback.message.answer_video(at.video_telegram_id)
        if not sent:
            await callback.message.answer('У вас не прикреплено ни одно видео')


@router.callback_query(F.data.startswith('files_view_note_'))
async def view_note_files(callback: CallbackQuery):
    await callback.answer()
    note_id = int(callback.data.replace("files_view_note_", ''))
    with Session(base.engine) as session:
        attachments = session.query(NoteAttachment).filter_by(note_id=note_id).all()
        sent = False
        for at in attachments:
            if at.file_telegram_id:
                sent = True
                await callback.message.answer_document(at.file_telegram_id)
        if not sent:
            await callback.message.answer('У вас не прикреплено ни одно видео')


@router.callback_query(F.data.startswith("delete_note_"))
async def delete_note(callback: CallbackQuery):
    await callback.answer()
    note_id = int(callback.data.replace("delete_note_", ''))
    with Session(base.engine) as session:
        note = session.query(TravelNote).filter_by(id=int(note_id)).first()
        title = str(note.title).strip().replace('\n', '')
        travel_id = str(note.travel_id)
        session.delete(note)
        session.commit()
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text='Назад', callback_data=f'view_notes_{travel_id}_0'))
        await callback.message.answer(f'Заметка \"{title}\" успешно удалена', reply_markup=builder.as_markup())
