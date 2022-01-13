from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):

    text = [
        'Список команд: ',
        '/menu - открыть меню',
        '/referrals - твои рефералы',
        '/send_photo - отправить нам свой скриншот',
        '/balance - посмотреть свой баланс',
        '/help - Получить справку'
    ]
    await message.reply('\n'.join(text))

