from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️Далее ", callback_data="next_page"),
     InlineKeyboardButton(text="Назад➡️", callback_data="prev_page")]
])