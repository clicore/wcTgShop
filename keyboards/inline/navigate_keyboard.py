from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️Назад", callback_data="prev_page"),
     InlineKeyboardButton(text="Далее➡", callback_data="next_page")]
])