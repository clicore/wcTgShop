import logging
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from loader import dp, bot, wcapi
from aiogram.dispatcher import filters, FSMContext
from misc import removeHTML
from states import States

@dp.message_handler(filters.Text("Корзина"), state='*')
async def showCart(message: Message, state=FSMContext):
    await States.Shopping.set()
    data = await state.get_data()
    if data.get("order"):
        if data["order"]["line_items"]:
            for i, item in enumerate(data["order"]["line_items"]):
                product = wcapi.get(f"products/{item['product_id']}").json()
                await bot.send_photo(message.from_user.id, product['images'][0]['src'],
                                     caption=f"<b><a href='{product['permalink']}'>{product['name']}</a></b>\n\n"
                                             f"{removeHTML(product['description'])}\n"
                                             f"Цена: {product['price']}$\n"
                                             f"Количество: {data['order']['line_items'][i]['quantity']} шт.",
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                         [InlineKeyboardButton(text="➕", callback_data=f"add:{i}"),
                                          InlineKeyboardButton(text="➖", callback_data=f"subtract:{i}")],
                                         [InlineKeyboardButton(text="Удалить", callback_data=f"delete:{i}")]
                                     ]))
            await message.answer("Благодарим Вас за выбор в нашем магазине! Желаете оформить заказ?",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [InlineKeyboardButton(text="Да, оформить заказ!", callback_data="order")]
                                 ]))
        else:
            await message.answer("Ваша корзина пуста! Для выбора товаров, перейдите в магазин.")
    else:
        await message.answer("Ваша корзина пуста! Для выбора товаров, перейдите в магазин.")

@dp.callback_query_handler(CallbackData("add", "param").filter(), state=States.Shopping)
async def addInCart(query: CallbackQuery, callback_data: dict, state=FSMContext):
    async with state.proxy() as proxy:
        product = wcapi.get(f"products/{proxy['order']['line_items'][int(callback_data.get('param'))]['product_id']}").json()
        proxy["order"]["line_items"][int(callback_data.get("param"))]["quantity"] += 1
        await query.message.edit_caption(caption=f"<b><a href='{product['permalink']}'>{product['name']}</a></b>\n\n"
                                                 f"{removeHTML(product['description'])}\n"
                                                 f"Цена: {product['price']}$\n"
                                                 f"Количество: {proxy['order']['line_items'][int(callback_data.get('param'))]['quantity']} шт.",
                                         reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                             [InlineKeyboardButton(text="➕", callback_data=f"add:{callback_data.get('param')}"),
                                              InlineKeyboardButton(text="➖",
                                                                   callback_data=f"subtract:{callback_data.get('param')}")],
                                             [InlineKeyboardButton(text="Удалить",
                                                                   callback_data=f"delete:{callback_data.get('param')}")]
                                         ]))
    await query.answer()


@dp.callback_query_handler(CallbackData("subtract", "param").filter(), state=States.Shopping)
async def addInCart(query: CallbackQuery, callback_data: dict, state=FSMContext):
    async with state.proxy() as proxy:
        if proxy["order"]["line_items"][int(callback_data.get("param"))]["quantity"] > 1:
            product = wcapi.get(f"products/{proxy['order']['line_items'][int(callback_data.get('param'))]['product_id']}").json()
            proxy["order"]["line_items"][int(callback_data.get("param"))]["quantity"] -= 1
            await query.message.edit_caption(caption=f"<b><a href='{product['permalink']}'>{product['name']}</a></b>\n\n"
                                                     f"{removeHTML(product['description'])}\n"
                                                     f"Цена: {product['price']}$\n"
                                                     f"Количество: {proxy['order']['line_items'][int(callback_data.get('param'))]['quantity']} шт.",
                                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                 [InlineKeyboardButton(text="➕",
                                                                       callback_data=f"add:{callback_data.get('param')}"),
                                                  InlineKeyboardButton(text="➖",
                                                                       callback_data=f"subtract:{callback_data.get('param')}")],
                                                 [InlineKeyboardButton(text="Удалить",
                                                                       callback_data=f"delete:{callback_data.get('param')}")]
                                             ]))
    await query.answer()

@dp.callback_query_handler(CallbackData("delete", "param").filter(), state=States.Shopping)
async def deleteFromCart(query: CallbackQuery, callback_data: dict, state=FSMContext):
    async with state.proxy() as proxy:
        proxy["order"]["line_items"].pop(int(callback_data.get("param")))
        await query.answer("Товар удалён из корзины!")
    await query.message.delete()