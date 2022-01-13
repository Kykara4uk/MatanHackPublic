import logging

from aiogram import Dispatcher

from data.config import  admins


async def on_startup_notify(dp: Dispatcher):
    pass

async def on_shutdown_notify(dp: Dispatcher):
    for admin in admins:
        try:
            await dp.bot.send_message(admin, "Бот выключен")

        except Exception as err:
            logging.exception(err)
