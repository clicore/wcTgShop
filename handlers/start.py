from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from loader import dp
from keyboards import main_keyboard
from states import States

@dp.message_handler(Command("start"), state='*')
async def start(message: Message):
    await States.Shopping.set()
    await message.answer("Добро пожаловать в магазин!", reply_markup=main_keyboard.keyboard)
    await message.delete()