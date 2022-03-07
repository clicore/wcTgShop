from aiogram.dispatcher.filters.state import StatesGroup, State

class States(StatesGroup):
    Shopping = State()
    Order = State()
    GetName = State()
    GetLastName = State()
    GetPhone = State()
    PaymentChoice = State()
    GetCard = State()
    GetCardDate = State()
    GetCVV = State()