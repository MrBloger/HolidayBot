from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from sqlalchemy.ext.asyncio import AsyncSession


from states import AddEvent, AddParticipant
from lexicon.lexicon import LEXICON

from keyboards.keyboards import (create_delete_events_kb, create_delete_participants_kb,
                                create_events_keyboard, create_my_events_for_participant_keyboard,
                                create_my_events_keyboard, create_participant_keyboard, 
                                create_choice_kb, delete_event_or_participant) 

from database.crud import (create_event, delete_events, delete_participants, edit_events, 
                            get_events, create_participants, get_participants_for_event)


router = Router()


# Этот хэндлер будет срабатывать на команду "/start"
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(LEXICON['/start'])
    # await message.answer_animation(
    #     'CgACAgIAAxkBAAIPbWfR0UpeyQonxHWDbUBSnG_ef1XFAALXbgACIdyQSuSjpL_qTdB1NgQ',
    #     caption=LEXICON['/start']
    # )


# Этот хэндлер будет срабатывать на команду "/help"
# и отправлять пользователю сообщение со списком доступных команд в боте
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON['/help'])


# Этот хэндлер будет срабатывать на команду "/cansel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands='cansel'), ~StateFilter(default_state))
async def process_cansel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text=LEXICON['cansel']
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()

# Этот хэндлер будет срабатывать на команду "/cansel_participant" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands='cansel_participant'), ~StateFilter(default_state))
async def process_cansel_participant_command_state(message: Message, state: FSMContext):
    await message.answer(
        text=LEXICON['cansel_participant']
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()

# Этот хэндлер будет срабатывать на команду /create_event
# и переводить бота в состояние оиждания ввода названия мероприятие
@router.message(Command(commands='create_event'))#, StateFilter(default_state))
async def process_create_event_command(message: Message, state: FSMContext):
    await message.answer(LEXICON['create_event'])
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(AddEvent.event_name)


# Этот хэндлер будет срабатывать, если введено корректное название
# и переводить в состояние ожидания ввода даты
@router.message(StateFilter(AddEvent.event_name), F.text)
async def process_name_sent(message: Message, state: FSMContext):
    
    # Cохраняем введенное имя в хранилище по ключу "event_name"
    await state.update_data(event_name=message.text)
    
    await message.answer(
        text=LEXICON['enter_date']
    )
    
    # Устанавливаем состояние ожидания ввода даты
    await state.set_state(AddEvent.event_date)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@router.message(StateFilter(AddEvent.event_name))
async def warning_not_event_name(message: Message):
    await message.answer(
        text=LEXICON['warning_not_event_name']
    )


# Этот хэндлер срабатывает, если введена корректная дата,
# а также обработка исключений.
@router.message(StateFilter(AddEvent.event_date))
async def process_event_date_sent(message: Message, session: AsyncSession, state: FSMContext):
    try:
        # Проверка, если сообщение не текстовое (например, гиф или видео)
        if message.text is None:
            raise ValueError("Сообщение не является текстом")
        
        # Пытаться преобразовать текст сообщения в дату
        event_date_str = message.text
        event_date = datetime.strptime(event_date_str, '%d/%m/%Y').date()

        # Сохраняем дату в хранилище по ключу "event_date"
        await state.update_data(event_date=event_date)

        # Извлекаем данные из состояния для получения имени мероприятия 
        data = await state.get_data()
        event_name = data.get('event_name')
        
        # Получаем ID пользователя, который отправил сообщение
        creator_id = message.from_user.id
        

        # Сохраняем событие в базе данных
        await create_event(session, event_name, event_date, creator_id)
        
        await message.answer(
            text=LEXICON['event_saved']
        )
        
        # Завершаем машину состояний
        await state.clear()

    except ValueError:
        # Если произошла ошибка преобразования даты, отправляем предупреждение
        await message.answer(
            text=LEXICON['warning_not_event_date']
        )


# Этот хэндлер срабатывает на команду "/edit_events" и
# и выдает пользователю список мероприятий.
@router.message(Command(commands='edit_events'))
async def process_edit_press(message: Message, session: AsyncSession):
    # Получаем id пользователя
    creator_id = message.from_user.id
    
    # Получаем события из базы данных
    events = await get_events(session, creator_id)
    
    # events = [await session.merge(event) for event in events]
    

    # Создаем клавиатуру с мероприятиями
    await message.answer(
        text=LEXICON['events_info'],
        reply_markup=create_events_keyboard(events)
    )


# Этот хэндлер срабатывает на кнопку "Изменить"
@router.callback_query(F.data == 'edit_events')
async def process_edit_events_press(callback: CallbackQuery, session: AsyncSession):
    
    creator_id = callback.from_user.id
    del_events = await get_events(session, creator_id)
    
    await callback.message.edit_text(
        text=LEXICON['delete_events_info'],
        reply_markup=delete_event_or_participant()
        # reply_markup=create_delete_events_kb(del_events)
    )
    
    await callback.answer()

# Этот хэндлер срабатывает на кнопку "❌ Мероприятие"
# и выдает список мероприятий к удалению.
@router.callback_query(F.data == 'delete_event')
async def process_event_delete(callback: CallbackQuery, session: AsyncSession):
    
    creator_id = callback.from_user.id
    del_events = await get_events(session, creator_id)
    
    await callback.message.edit_text(
        text=f'❌ Вы моежете удалить мероприятие',
        reply_markup=create_delete_events_kb(del_events)
    )
    
    await callback.answer()


# Этот хэндлер срабатывает на кнопку "❌ Участников"
# и выдает список мероприятий к удалению.
@router.callback_query(F.data == 'delete_participant')
async def process_participant_delete(callback: CallbackQuery, session: AsyncSession):
    
    creator_id = callback.from_user.id
    events = await get_events(session, creator_id)
    
    await callback.message.edit_text(
        text=f'Выберите мероприятия для продолжения',
        reply_markup=create_my_events_for_participant_keyboard(events)
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith("del_participant_for_event:"))
async def process_del_participant_for_event(callback: CallbackQuery, session: AsyncSession):
    
    event_id = int(callback.data.split(':')[1])
    
    # Запрашиваем из базы данных участников, созданные пользователем
    del_participants = await get_participants_for_event(session, event_id)
    
    await callback.message.edit_text(
        text=f'❌ Вы можете удалить участников',
        reply_markup=create_delete_participants_kb(del_participants)
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith("participant_delete:"))
async def process_participant_delete_press(callback: CallbackQuery, session: AsyncSession):
    
    data_parts = callback.data.split(':')
    participant_id, event_id = data_parts[1], data_parts[2]
    
    await delete_participants(session, int(participant_id), int(event_id))
    
    updated_participants = await get_participants_for_event(session, int(event_id))
    
    # Обновляем клавиатуру с новыми данными
    await callback.message.edit_text(
        text=LEXICON['participant_deleted'],
        reply_markup=create_delete_participants_kb(updated_participants)
    )
    await callback.answer()


# Этот хэндлер срабатывает на кнопку "Назад"
# этого хэндлера "process_edit_events_press".
@router.callback_query(F.data == 'back_participant_delete')
async def process_back_participant_delete(callback: CallbackQuery):

    await callback.message.edit_text(
        text=LEXICON['delete_events_info'],
        reply_markup=delete_event_or_participant()
    )
    await callback.answer()


# Этот хэндлер срабатывает на инлайн-кнопку "❌ Отмена"
# и отображает список мероприятий.
@router.callback_query(F.data == 'cancel_delete')
async def process_cansel_delete_press(callback: CallbackQuery, session: AsyncSession):
    
    creator_id = callback.from_user.id
    events = await get_events(session, creator_id)
    
    
    await callback.message.edit_text(
        text=LEXICON['events_info'],
        reply_markup=create_events_keyboard(events)
    )
    
    await callback.answer()


# Этот хэндлер срабатывает на кнопку удаления мероприятия
# и предлагает дальнейшие действия.
@router.callback_query(F.data.startswith("event_delete:"))
async def process_delete_press(callback: CallbackQuery, session: AsyncSession):
    
    # Извлекаем ID мероприятия из callback-данных
    event_id = int(callback.data.split(':')[1])
    
    # Получаем id пользователя
    creator_id = callback.from_user.id
    
    await delete_events(session, creator_id, event_id)
    
    # Получаем обновленный список мероприятий
    del_events = await get_events(session, creator_id)
    
    await callback.message.edit_text(
        text=LEXICON['event_delete'],
        reply_markup=create_delete_events_kb(del_events)
    )
    
    await callback.answer()


# Этот хэндлер срабатывает при выборе мероприятия командой "/edit_events".
# Он отправляет пользователю клавиатуру с вариантами дальнейших действий:
# вернуться назад или добавить пользователя.
@router.callback_query(F.data.startswith("event_edit:"))
async def process_event_press(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    
    # Извлекаем ID мероприятия из callback-данных
    event_id = int(callback.data.split(':')[1])

    event = await edit_events(session, event_id)
    
    # Сохраняем event_id в хранилище
    await state.update_data(event_id=event_id)
    
    await callback.message.edit_text(
        text=f'{LEXICON["event_selected"]} {event.title}',
        reply_markup=create_choice_kb(event)
    )
    await callback.answer()


# Этот хэндлер будет срабатывать на кнопку "Назад"
# и возвращать прошлое сообщение
@router.callback_query(F.data == 'choice_back')
async def process_choice_back_press(callback: CallbackQuery, session: AsyncSession):
    # Получаем ID пользователя (создателя мероприятий)
    creator_id = callback.from_user.id

    # Загружаем список мероприятий пользователя
    events = await get_events(session, creator_id)

    # Обновляем сообщение (меняем текст + клавиатуру)
    await callback.message.edit_text(
        text=LEXICON['events_info'],
        reply_markup=create_events_keyboard(events)
    )
    await callback.answer()


# Этот хэндлер будет срабатывать на кнопку "Добавить"
# и переводить в состояние ожидания ввода имени участника.
@router.callback_query(F.data == 'add', StateFilter(default_state))
async def process_add_press(callback: CallbackQuery, state: FSMContext):
    
    prompt_message = await callback.message.edit_text(
        text=LEXICON['enter_participant_name']
    )
    
    # Сохраняем ID этого сообщения в состояние.
    await state.update_data(prompt_message_id=prompt_message.message_id)
    
    # Устанавливаем состояние ожидания ввода имени участника
    await state.set_state(AddParticipant.participant_name)
    
    await callback.answer()


# Этот хэндлер будет срабатывать, если введено корректное имя
# участника. # (и переводить в состояние ожидания ввода статуса, пока что не сделано)
@router.message(StateFilter(AddParticipant.participant_name))
async def process_alias_sent(message: Message, session: AsyncSession, state: FSMContext):
    
    # Получаем ID сохраненного сообщения с запросом
    data = await state.get_data()
    prompt_message_id = data.get('prompt_message_id')

    # Если ID найден, удаляем старое сообщение
    if prompt_message_id:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_message_id)
    
    # Cохраняем введенное имя в хранилище по ключу "participant_name"
    await state.update_data(participant_name=message.text)

    # Извлекаем данные из состояния
    data = await state.get_data()
    participant_name = data.get('participant_name')
    event_id = data.get('event_id')
    
    
    # Сохраняем участника в бд
    await create_participants(session, event_id, participant_name)
    
    await message.answer(
        text=LEXICON['participant_added']
    )

    await state.clear()


# Этот хэндлер срабатывает на команду "/my_events" 
# и выдает список ранее созданных мероприятий.
@router.message(Command(commands='my_events'))
async def process_my_events_command(message: Message, session: AsyncSession):
    
    # Получаем ID пользователя, отправившего команду
    creator_id = message.from_user.id 

    # Запрашиваем из базы данных мероприятия, созданные пользователем
    events = await get_events(session, creator_id)
    
    events = [await session.merge(event) for event in events]
    
    # Отправляем пользователю список его мероприятий с кнопками
    await message.answer(
        '🥳 <b>Ваши мероприятия:</b> 🎉',
        reply_markup=create_my_events_keyboard(events)
    )


# Этот хэндлер срабатывает на инлайн-кнопку созданного мероприятия
# и выдает список участников, ранее записанных в мероприятие команды "/my_events".
@router.callback_query(F.data.startswith("event:"))
async def process_def_event_press(callback: CallbackQuery, session: AsyncSession):
    
    # Извлекаем ID мероприятия из callback-данных
    event_id = int(callback.data.split(':')[1])
    
    # Запрашиваем из базы данных участников, созданные пользователем
    participant = await get_participants_for_event(session, event_id)
    
    # Отправляем пользователю список участников с кнопками
    await callback.message.edit_text(
        text=f'😇 <b>Участники мероприятия:</b> 🎁',
        reply_markup=create_participant_keyboard(participant)
    )
    await callback.answer()


# Этот хэндлер срабатывает на инлайн-кнопку "Назад" функции process_def_event_press
# и возвращает пользователя на прошлое сообщение


# Этот хэндлер срабатывает на инлайн-кнопку "Назад"
# и возвращает пользователя на прошлое сообщение
@router.callback_query(F.data =='home_back')
async def process_back_press(callback: CallbackQuery, session: AsyncSession):
    # Получаем ID пользователя
    creator_id = callback.from_user.id 

    # Загружаем список мероприятий пользователя
    events = await get_events(session, creator_id)

    # Изменяем текущее сообщение, обновляя текст и клавиатуру
    await callback.message.edit_text(
        text='🥳 <b>Ваши мероприятия:</b> 🎉',
        reply_markup=create_my_events_keyboard(events)
    )

    await callback.answer()
    
