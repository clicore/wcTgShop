from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from loader import bot, dp, wcapi
from aiogram import filters
from misc import removeHTML
from states import States
from keyboards.inline import navigate_keyboard

@dp.message_handler(filters.Text("Магазин"), state='*')
async def showProducts(message: Message, state=FSMContext):
    await States.Shopping.set()
    async with state.proxy() as proxy:
        if not proxy.get("shop"):
            proxy.update({"shop": {
                "page": 1,
                "message": []
            }})
        products = wcapi.get("products", params={"per_page": 5, "page": proxy["shop"]["page"]}).json()
        if proxy["shop"]["message"]:
            for msg in proxy["shop"]["message"]:
                await  bot.delete_message(message.from_user.id, msg)
            proxy["shop"]["message"] = []
        for product in products:
            msg = await bot.send_photo(message.from_user.id, product['images'][0]['src'],
                                        caption=f"<b><a href='{product['permalink']}'>{product['name']}</a></b>\n\n"
                                                f"{removeHTML(product['description'])}\n"
                                                f"Цена: {product['price']}$",
                                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                            [InlineKeyboardButton(text="В корзину", callback_data=f"cart:{product['id']}")]
                                        ]))
            proxy["shop"]["message"].append(msg["message_id"])
        msg = await message.answer("Для навигации используйте кнопки:", reply_markup=navigate_keyboard.keyboard)
        proxy["shop"]["message"].append(msg["message_id"])


@dp.callback_query_handler(text="next_page", state=States.Shopping)
async def nextPage(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as proxy:
        proxy["shop"].update({"page": proxy["shop"]["page"] + 1})
        products = wcapi.get("products", params={"per_page": 5, "page": proxy["shop"]["page"]}).json()
        if products:
            if proxy["shop"]["message"]:
                for msg in proxy["shop"]["message"]:
                    await  bot.delete_message(query.from_user.id, msg)
                proxy["shop"]["message"] = []
            for product in products:
                msg = await bot.send_photo(query.from_user.id, product['images'][0]['src'],
                                           caption=f"<b><a href='{product['permalink']}'>{product['name']}</a></b>\n\n"
                                                   f"{removeHTML(product['description'])}\n"
                                                   f"Цена: {product['price']}$",
                                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                               [InlineKeyboardButton(text="В корзину",
                                                                     callback_data=f"cart:{product['id']}")]
                                           ]))
                proxy["shop"]["message"].append(msg["message_id"])
            msg = await query.message.answer("Для навигации используйте кнопки:", reply_markup=navigate_keyboard.keyboard)
            proxy["shop"]["message"].append(msg["message_id"])
        else:
            if proxy["shop"]["page"] > 1:
                proxy["shop"]["page"] -= 1
    await query.answer()

@dp.callback_query_handler(text="prev_page", state=States.Shopping)
async def prevPage(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as proxy:
        if proxy["shop"]["page"] > 1:
            proxy["shop"].update({"page": proxy["shop"]["page"] - 1})
            products = wcapi.get("products", params={"per_page": 5, "page": proxy["shop"]["page"]}).json()
            if not products:
                if proxy["shop"]["page"] > 1:
                    proxy["shop"]["page"] -= 1
                    products = wcapi.get("products?per_page=5&page=" + str(proxy["shop"]["page"])).json()
            if proxy["shop"]["message"]:
                for msg in proxy["shop"]["message"]:
                    await  bot.delete_message(query.from_user.id, msg)
                proxy["shop"]["message"] = []
            for product in products:
                msg = await bot.send_photo(query.from_user.id, product['images'][0]['src'],
                                           caption=f"<b><a href='{product['permalink']}'>{product['name']}</a></b>\n\n"
                                                   f"{removeHTML(product['description'])}\n"
                                                   f"Цена: {product['price']}$",
                                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                               [InlineKeyboardButton(text="В корзину",
                                                                     callback_data=f"cart:{product['id']}")]
                                           ]))
                proxy["shop"]["message"].append(msg["message_id"])
            msg = await query.message.answer("Для навигации используйте кнопки:", reply_markup=navigate_keyboard.keyboard)
            proxy["shop"]["message"].append(msg["message_id"])
    await query.answer()

@dp.callback_query_handler(CallbackData("cart", "param").filter(), state=States.Shopping)
async def addToCart(query: CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as proxy:
        if not proxy.get("order"):
            proxy.update({"order": {
                "payment_method": "bacs",
                "payment_method_title": "",
                "set_paid": False,
                "billing": {
                    "first_name": "",
                    "last_name": "-",
                    "address_1": "",
                    "address_2": "",
                    "city": "Запорожье",
                    "state": "Украина",
                    "postcode": "69000",
                    "country": "Украина",
                    "email": "example@mail.ru",
                    "phone": ""
                },
                "shipping": {
                    "first_name": "",
                    "last_name": "",
                    "address_1": "",
                    "address_2": "",
                    "city": "",
                    "state": "",
                    "postcode": "",
                    "country": ""
                },
                "line_items": [],
                "shipping_lines": [],
                "meta_data": [
                    {
                        "id": 0,
                        "key": "user_id",
                        "value": str(query.from_user.id)
                    }
                ]
            }})
        isProductExists = False
        for i, product in enumerate(proxy["order"]["line_items"]):
            if product["product_id"] == int(callback_data.get("param")):
                proxy["order"]["line_items"][i]["quantity"] += 1
                isProductExists = True
                break
        if not isProductExists:
            proxy["order"]["line_items"].append({
                "product_id": int(callback_data.get("param")),
                "quantity": 1
            })
    await query.answer()