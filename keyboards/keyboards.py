from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callback_factory import UserAction, UserActionCall
from lexicon.lexicon import LEXICON


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# продолжить кориектировку отсюда
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# Выдает список ранее созданых мероприятий
# с кнопкой "Изменить"
def create_events_keyboard(events) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    for event in events:
        event_id = event.id
        title = event.title
        kb_builder.row(InlineKeyboardButton(
            text=title,
            callback_data=f'event_edit:{event_id}'
        ))
    
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['edit_events_button'],
            callback_data='edit_events'
        ),
        width=2
    )
    
    return kb_builder.as_markup()


# Выдает клавиатуру с кнопкой "Назад" и "Добавить" - участников
def create_choice_kb(event) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['back'],
            callback_data='choice_back'
        ),
        InlineKeyboardButton(
            text=LEXICON['add'],
            callback_data='add'
        ),
        width=2
    )
    
    return kb_builder.as_markup()


# Выдает список мероприятий
def create_my_events_keyboard(events) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    
    for event in events:
        event_id = event.id
        title = event.title
        kb_builder.row(
            InlineKeyboardButton(
                text=title,
                callback_data=f'event:{event_id}'
            )
        )
    
    # kb_builder.row(
    #     InlineKeyboardButton(
    #         text=LEXICON['back'],
    #         callback_data='back_participant_delete'
    #     )
    # )
    
    return kb_builder.as_markup()


# Выдает список участников
def create_participant_keyboard(participants) -> InlineKeyboardMarkup:
    # Создаем объект клавиатуры
    kb_builder = InlineKeyboardBuilder()
    
    # Заполняем список кнопками с именами участников
    buttons = [
        InlineKeyboardButton(
            text=participant.username,
            callback_data=f'username:{participant.username}'
        )
        for participant in participants
    ]

    # Добавляем кнопки участников с шириной 2 (две колонки)
    kb_builder.row(*buttons, width=2)

    # Добавляем кнопку "Назад" отдельной строкой
    kb_builder.row(InlineKeyboardButton(text=LEXICON['back'], callback_data='home_back'))

    return kb_builder.as_markup()


# Выдает список мероприятий к удалению
def create_delete_events_kb(del_events) -> InlineKeyboardMarkup:
    # Создаем объект клавиатуры
    kb_builder = InlineKeyboardBuilder()
    
    for event in del_events:
        event_id = event.id
        title = event.title
        kb_builder.row(InlineKeyboardButton(
            text=f'❌ {title}',
            callback_data=f'event_delete:{event_id}'
        ))
    
    # Добавляем кнопку "Отмена"
    kb_builder.row(
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data='back_participant_delete'
        )
    )
    
    return kb_builder.as_markup()


def create_delete_participants_kb(del_participants) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    
    # Заполняем список кнопками с именами участников
    buttons = [
        InlineKeyboardButton(
            text=f'❌ {participant.username}',
            callback_data=f'participant_delete:{participant.id}:{participant.event_id}'
        )
        for participant in del_participants
    ]

    # Добавляем кнопки участников с шириной 2 (две колонки)
    kb_builder.row(*buttons, width=2)
    
    kb_builder.row(
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data='back_participant_delete'
            )
    )
    return kb_builder.as_markup()


def delete_event_or_participant() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    
    kb_builder.row(
        InlineKeyboardButton(
            text=f'❌ Мероприятие',
            callback_data='delete_event'
        ),
        InlineKeyboardButton(
            text=f'❌ Участники',
            callback_data='delete_participant'
        ),
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data='cancel_delete'
        ),
        width=2
    )
    
    return kb_builder.as_markup()


def create_my_events_for_participant_keyboard(events) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    
    for event in events:
        event_id = event.id
        title = event.title
        kb_builder.row(
            InlineKeyboardButton(
                text=title,
                callback_data=f'del_participant_for_event:{event_id}'
            )
        )
    
    kb_builder.row(
        InlineKeyboardButton(
            text=LEXICON['back'],
            callback_data='back_participant_delete'
        )
    )
    
    return kb_builder.as_markup()

# async def create_event_kb():
#     start_kb = InlineKeyboardBuilder()
#     start_kb.add(
#         InlineKeyboardButton(text=LEXICON[''])
#         InlineKeyboardButton(text=LEXICON['create_event'], callback_data=UserActionCall(action=UserAction.add_event).pack())
        
#     start_kb.adjust(2)
    
#     return start_kb.as_markup()

# async def create_event_kb():
#     kb_builder = InlineKeyboardBuilder()
#     kb_builder.row(
#         InlineKeyboardButton(text=LEXICON['create_event'], callback_data=UserActionCall(action=UserAction.add_event).pack()),
#         InlineKeyboardButton(text=LEXICON['create_event'], callback_data=UserActionCall(action=UserAction.add_event).pack()),
#         InlineKeyboardButton(text=LEXICON['create_event'], callback_data=UserActionCall(action=UserAction.add_event).pack()),
#         width=2)
    
#     return kb_builder.as_markup()



# async def create_event_kb(session: AsyncSession):
#     async with session as session:
#         create_event = await crud.get_or_create_event(session, event_name=message.text, user_id=message.from_user.id)
#         kb = InlineKeyboardBuilder()
#         kb.add(InlineKeyboardButton(text='Нет доступных', callback_data=UserActionCall(action=UserAction.add_event).pack()))
#         return kb.as_markup()
