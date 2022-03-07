from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup([
    [KeyboardButton(text="Приват24")],
    [KeyboardButton(text="Оплата картой")],
    [KeyboardButton(text="Наличные при получении")],
    [KeyboardButton(text="Назад")],
    [KeyboardButton(text="Отменить оформление заказа")]
])