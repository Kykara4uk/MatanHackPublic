from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from handlers.users.menu_handlers import show_menu
from loader import dp, bot
from utils.db_api.db_commands import add_user, get_user


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer_sticker(sticker="CAACAgQAAxkBAAIGXV__bWFhszPnWYSQJvKthQoMiem8AAJrAAPOOQgNWWbqY3aSS9AeBA")
    user = types.User.get_current()
    tg_id = user.id
    isUserAlreadyInDB = await get_user(tg_id)
    if isUserAlreadyInDB==None:
        first_name = user.first_name
        full_name = user.full_name
        bot_username = (await bot.get_me()).username
        referal_code = "https://t.me/{bot_username}?start={tg_id}".format(bot_username=bot_username, tg_id=tg_id)
        username = user.username
        referal_p = message.get_args()
        referal = None
        balance = "150"
        isReferalActivated = True
        if referal_p:
            if not int(referal_p) == tg_id:
                referal = int(referal_p)
                isReferalActivated = False
                balance = "200"
        await add_user(tg_id=tg_id, first_name=first_name, full_name=full_name, balance=balance, referal_code=referal_code, referal=referal, username=username, isReferalActivated=isReferalActivated)
    await message.answer(f'Привет, {message.from_user.first_name}!'
                         f' Этот бот поможет найти ответы на мудл по матанализу')
    await show_menu(message)

