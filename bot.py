import asyncio
from aiogram import executor
from handlers import dp
from loader import bot, app, routes
from aiogram.dispatcher.webhook import web, configure_app
import config

async def on_startup():
    await bot.set_webhook(config.SERVER_URL + "/bot")
    configure_app(dp, app, "/bot")
    app.add_routes(routes)

async def on_shutdown():
    await bot.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, port=8080, access_log=None)
    #executor.start_polling(dp, skip_updates=True) # временно