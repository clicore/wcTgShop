from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("Магазин")],
    [KeyboardButton("Корзина")],
    [KeyboardButton("Акции")],
    [KeyboardButton("О нас")]
], resize_keyboard=True)