import config
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiohttp import web
from woocommerce import API
from liqpay.liqpay import LiqPay
logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
app = web.Application()
routes = web.RouteTableDef()
liqpay = LiqPay(config.LIQPAY_PUBLIC, config.LIQPAY_PRIVATE)
wcapi = API(
    url=config.API_URL,
    consumer_key=config.CONSUMER_KEY,
    consumer_secret=config.CONSUMER_SECRET,
    version=config.API_VERSION
)