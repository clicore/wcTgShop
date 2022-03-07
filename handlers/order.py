import base64
import json
import random
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import CallbackQuery, Message
from aiohttp import web
from loader import dp, bot, routes, liqpay, wcapi
import config
from states import States
from keyboards import payment_keyboard, back_keyboard, getphone_keyboard
from handlers import start


@dp.callback_query_handler(text="order", state='*')
async def makeOrder(query: CallbackQuery, state=FSMContext):
    await States.Order.set()
    async with state.proxy() as proxy:
        proxy.update({"payment": {
            "amount": "0",
            "card": "",
            "card_exp_month": "",
            "card_exp_year": "",
            "card_cvv": ""
        }})
        if proxy["order"]["line_items"]:
            for i, item in enumerate(proxy["order"]["line_items"]):
                product = wcapi.get(f"products/{item['product_id']}").json()
                proxy["payment"]["amount"] = str(float(proxy["payment"]["amount"]) + (float(product["price"]) * item["quantity"]))
        if float(proxy["payment"]["amount"]) > 0:
            await query.message.answer(f"Итоговая сумма заказа ${proxy['payment']['amount']}\n\n"
                                       "🔸 Убедитесь что всё верно, в ином случае вы можете вернуться обратно в магазин!\n"
                                       "🔸 При оформлении заказа требуется вводить настоящие данные, в противном случае заказ будет отменён!\n\n"
                                       "Теперь введите ваше полное имя?",
                                       reply_markup=back_keyboard.back_button)
            await States.next()
        else:
            await query.answer("Ошибка операции!")
    await query.answer()

@dp.message_handler(filters.Text("Вернуться в магазин"), state='*')
@dp.message_handler(filters.Text("Отменить оформление заказа"), state='*')
async def toStore(message: Message):
    await start.start(message)

@dp.message_handler(state=States.GetName)
async def getName(message: Message, state=FSMContext):
    if message.text == "Назад":
        await start.start(message)
    else:
        await States.next()
        async with state.proxy() as proxy:
            proxy["order"]["billing"]["first_name"] = message.text
            proxy["order"]["shipping"]["first_name"] = message.text
        await message.answer("Введите вашу фамилию?", reply_markup=back_keyboard.cancel_order)

@dp.message_handler(state=States.GetLastName)
async def getLastName(message: Message, state=FSMContext):
    if message.text == "Назад":
        await States.previous()
        await message.answer("Введите ваше полное имя?", reply_markup=back_keyboard.back_button)
    else:
        await States.next()
        async with state.proxy() as proxy:
            proxy["order"]["billing"]["last_name"] = message.text
            proxy["order"]["shipping"]["last_name"] = message.text
        await message.answer("Нам потребуется ваш номер телефона, желаете отправить номер телефона?", reply_markup=getphone_keyboard.keyboard)


@dp.message_handler(content_types="contact", state=States.GetPhone)
async def getPhone(message: Message, state=FSMContext):
    if message.text == "Назад":
        await States.previous()
        await message.answer("Введите вашу фамилию?", reply_markup=back_keyboard.cancel_order)
    else:
        await States.next()
        async with state.proxy() as proxy:
            proxy["order"]["billing"]["phone"] = message.contact.phone_number
        await message.answer("Выберите способ оплаты?", reply_markup=payment_keyboard.keyboard)

@dp.message_handler(state=States.PaymentChoice)
async def paymentChoice(message: Message, state=FSMContext):
    if message.text == "Назад":
        await States.previous()
        await message.answer("Введите ваш номер телефона?", reply_markup=back_keyboard.cancel_order)
    else:
        async with state.proxy() as proxy:
            if message.text == "Приват24":
                proxy["order"]["payment_method_title"] = "LiqPay Invoice Bot"
                order = wcapi.post("orders", proxy["order"]).json()
                payment = liqpay.api("request", {
                    "action": "invoice_bot",
                    "version": "3",
                    "amount": proxy["payment"]["amount"],
                    "currency": "USD",
                    "order_id": str(random.randint(10000000, 99999999)),
                    "phone": proxy["order"]["billing"]["phone"],
                    "description": str(order["id"]),
                    "server_url": config.SERVER_URL.replace("https", "http") + "/callback"
                })
                if payment["result"] == "ok":
                    proxy["order"] = {}
                    await state.finish()
                    await message.answer("Платёж был отправлен на ваш аккаунт Приват24. "
                                         "Вы можете воспользоваться приложением, чтобы подтвердить платёж!")
                else:
                    wcapi.delete("orders/" + str(order["id"]), params={"force": True}).json()
                    await message.answer("Произошла ошибка, убедитесь в корректности предоставленных данных при оформлении заказа!")
            if message.text == "Оплата картой":
                proxy["order"]["payment_method_title"] = "LiqPay Pay"
                await States.next()
                await message.answer("Введите номер вашей карты?", reply_markup=back_keyboard.cancel_order)
            if message.text == "Наличные при получении":
                order = wcapi.post("orders", proxy["order"]).json()
                await message.answer("Благодарим за заказ!\n\n"
                                     f"Номер вашего заказа: {order['number']}\n\n"
                                     "Наш персонал в ближайшее рабочее время свяжется с вами для уточнения подробностей. "
                                     "Запомните или запишите номер вашего заказа, на случай каких либо ошибок!",
                                     reply_markup=back_keyboard.to_store)
                proxy["order"] = {}
                await state.finish()

@dp.message_handler(state=States.GetCard)
async def getCard(message: Message, state=FSMContext):
    if message.text == "Назад":
        await States.previous()
        await message.answer("Выберите способ оплаты?", reply_markup=payment_keyboard.keyboard)
    else:
        await States.next()
        async with state.proxy() as proxy:
            proxy["payment"]["card"] = message.text
        await message.answer("Введите срок действия вашей карты в таком же формате, как написано на карте бех пробелов(например 09/22)?")

@dp.message_handler(state=States.GetCardDate)
async def getCardMonth(message: Message, state=FSMContext):
    if message.text == "Назад":
        await States.previous()
        await message.answer("Введите номер вашей карты?", reply_markup=back_keyboard.cancel_order)
    else:
        await States.next()
        async with state.proxy() as proxy:
            proxy["payment"]["card_exp_month"] = message.text[0:2]
            proxy["payment"]["card_exp_year"] = message.text[3:len(message.text)]
        await message.answer("Введите CVV код карты?")

@dp.message_handler(state=States.GetCVV)
async def getCardCVV(message: Message, state=FSMContext):
    if message.text == "Назад":
        await States.previous()
        await message.answer("Введите срок действия вашей карты в таком же формате, как написано на карте бех пробелов(например 09/22)?")
    else:
        async with state.proxy() as proxy:
            proxy["payment"]["card_cvv"] = message.text
            order = wcapi.post("orders", proxy["order"]).json()
            payment = liqpay.api("request", {
                "action": "pay",
                "version": "3",
                "phone": proxy["order"]["billing"]["phone"],
                "amount": proxy["payment"]["amount"],
                "currency": "USD",
                "description": str(order["id"]),
                "order_id": str(random.randint(10000000, 99999999)),
                "card": proxy["payment"]["card"],
                "card_exp_month": proxy["payment"]["card_exp_month"],
                "card_exp_year": proxy["payment"]["card_exp_year"],
                "card_cvv": proxy["payment"]["card_cvv"],
                "server_url": config.SERVER_URL.replace("https", "http") + "/callback"
            })
            if payment["result"] == "ok":
                proxy["order"] = {}
                await state.finish()
            else:
                wcapi.delete("orders/" + str(order["id"]), params={"force": True}).json()
                await message.answer("Произошла ошибка, убедитесь в корректности предоставленных данных при оформлении заказа!")

@routes.post('/callback')
async def liqpayCallback(request: web.Request):
    body = await request.post()
    sign = liqpay.str_to_sign(config.LIQPAY_PRIVATE + body.get("data") + config.LIQPAY_PRIVATE)
    if sign.decode("utf8") == body.get("signature"):
        data = json.loads(base64.b64decode(body.get("data")).decode('utf-8'))
        wcapi.post("orders/"+str(data["description"]), {"status": "processing"})
        order = wcapi.get("orders/"+str(data["description"])).json()
        await bot.send_message(order["meta_data"][0]["value"], "Благодарим за заказ!\n\n"
                                     f"Номер вашего заказа: {order['number']}\n\n"
                                     "Наш персонал в ближайшее рабочее время свяжется с вами для уточнения подробностей. "
                                     "Запомните или запишите номер вашего заказа, на случай каких либо ошибок!",
                                     reply_markup=back_keyboard.to_store)
    return web.Response(text=sign.decode("utf8"))