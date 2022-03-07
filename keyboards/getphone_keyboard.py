from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("Отправить телефон", request_contact=True)],
    [KeyboardButton("Назад")]
], resize_keyboard=True)