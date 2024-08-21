from aiogram.fsm.state import State, StatesGroup

class CreateTravel(StatesGroup):
    title = State()
    description = State()

class CreateLocation(StatesGroup):
    location = State()

class AlterTitle(StatesGroup):
    title = State()

class AlterDescription(StatesGroup):
    description = State()

class AddTravelPartner(StatesGroup):
    partner = State()

class CreateNote(StatesGroup):
    title = State()
    photo = State()
    video = State()
    file = State()
    text = State()

class SplitBuy(StatesGroup):
    user = State()
    money_need = State()
    money = State()
