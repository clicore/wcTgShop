from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

back_button = ReplyKeyboardMarkup([
    [KeyboardButton("Назад")]
], resize_keyboard=True)

cancel_order = ReplyKeyboardMarkup([
    [KeyboardButton("Назад")],
    [KeyboardButton("Отменить оформление заказа")]
], resize_keyboard=True)

to_store = ReplyKeyboardMarkup([
    [KeyboardButton("Вернуться в магазин")]
], resize_keyboard=True)