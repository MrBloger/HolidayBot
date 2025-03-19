from aiogram.fsm.state import State, StatesGroup

class AddEvent(StatesGroup):
    event_name = State()
    event_date = State()

class AddParticipant(StatesGroup):
    participant_name = State()
    # participant_status = State()