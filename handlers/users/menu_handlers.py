from functools import wraps
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from handlers.users.states import NewScreenshot, WriteToAdmins
from keyboards.inline.menu_keyboards import tests_keyboard, exercises_keyboard, screenshots_keyboard, \
    menu_cd, first_keyboard, earn_keyboard, make_callback_data, confirm_entrance_keyboard, not_enough_money_keyboard, \
    confirm_exit_keyboard, answer_keyboard
from loader import dp, bot
from utils.db_api.db_commands import get_referrals, get_referral_link, get_screenshot, get_screenshots, get_test_name, \
    change_money, get_user, check_money, get_tests, get_exercise, get_test_code, get_exercise_code, get_referral_status, \
    activate_referal, vidminok, get_unchaked_screenshots
from utils.db_api.models import Screenshots
from data.config import ADMIN_CHAT_ID, admins
import asyncio

@dp.message_handler(chat_type=types.ChatType.GROUP, is_reply=True, commands=["b"], content_types=types.ContentType.TEXT)
async def group_change_money(message: types.Message):
    user = types.User.get_current().id
    if str(user) in admins:
        if message.chat.id == int(ADMIN_CHAT_ID):
            if message.reply_to_message != None and message.reply_to_message.forward_from != None:
                
                user_mess_id = message.reply_to_message.forward_from.id
                
                async def command_b_changeUserBalance(money_to_change):
                    await change_money(money_to_change, user_mess_id)
                    user = await get_user(user_mess_id)

                    if money_to_change<0:
                        try: 
                            await bot.send_message(chat_id=user_mess_id, text='С твоего счета было снято '+await vidminok(money_to_change)+' администратором\nТекущий баланс: '+await vidminok(user.balance))
                        except:pass 
                    else:
                        try:   
                            await bot.send_message(chat_id=user_mess_id, text='На твой счёт поступило '+await vidminok(money_to_change)+' от администратора\nТекущий баланс: '+await vidminok(user.balance))
                        except:pass 
                    text = 'Баланс ' + '<a href="tg://user?id=' + str(
                            user.tg_id) + '">' + user.full_name + '</a>' + ' = ' + user.balance + ' (' + str(money_to_change) + ')'
                    await message.reply(text=text)
                    
                try:
                    message_array = message.text.split(" ")
                    money_to_change = int(message_array[-1])
                    await command_b_changeUserBalance(money_to_change)
                except: 
                    await message.reply(text='Введи правильную сумму')


@dp.message_handler(commands=["b"], content_types=types.ContentType.TEXT)
async def change_money_b(message: types.Message):
    user = types.User.get_current().id
    if str(user) in admins:
        mess = message.text
        messArray = mess.split(" ")
        try:
            user_db = await get_user(int(messArray[1]))

            if user_db!= None:
                async def command_b_changeUserBalance(money_to_change, user_db):
                    await change_money(money_to_change, user_db.tg_id)

                    if money_to_change < 0:
                        try:
                            await bot.send_message(chat_id=user_db.tg_id,
                                                   text='С твоего счета было снято ' + await vidminok(
                                                       money_to_change) + ' администратором\nТекущий баланс: ' + await vidminok(
                                                       user_db.balance))
                        except:
                            pass
                    else:
                        try:
                            await bot.send_message(chat_id=user_db.tg_id,
                                                   text='На твой счёт поступило ' + await vidminok(
                                                       money_to_change) + ' от администратора\nТекущий баланс: ' + await vidminok(
                                                       user_db.balance))
                        except:
                            pass
                    text = 'Баланс ' + '<a href="tg://user?id=' + str(
                        user_db.tg_id) + '">' + user_db.full_name + '</a>' + ' = ' + user_db.balance + ' (' + str(
                        money_to_change) + ')'
                    await message.reply(text=text)

                try:
                    message_array = message.text.split(" ")
                    money_to_change = int(message_array[-1])
                    await command_b_changeUserBalance(money_to_change, user_db)
                except:
                    await message.reply(text='Введи правильную сумму')
            else:
                await message.reply(text='Неверный формат команды - /b tg_id money')
        except:
            await message.reply(text='Ошибка с telegram id')



                


@dp.message_handler(chat_type=types.ChatType.GROUP, is_reply=True, content_types=types.ContentType.TEXT)
async def group(message: types.Message):
    user = types.User.get_current().id
    if str(user) in admins:
        if message.chat.id == int(ADMIN_CHAT_ID):
            if message.reply_to_message != None and message.reply_to_message.forward_from != None:
                user_mess_id = message.reply_to_message.forward_from.id
                await bot.send_message(chat_id=user_mess_id, text=message.text,
                                       reply_to_message_id=message.reply_to_message.forward_from_message_id)
                await message.reply(text="Отправлено 🕊")


@dp.message_handler(chat_type=types.ChatType.GROUP, is_reply=True, content_types=types.ContentType.STICKER)
async def groupp(message: types.Message):
    user = types.User.get_current().id
    if str(user) in admins:
        if message.chat.id == int(ADMIN_CHAT_ID):
            if message.reply_to_message != None and message.reply_to_message.forward_from != None:
                user_mess_id = message.reply_to_message.forward_from.id
                sticker = message.sticker.file_id
                await bot.send_sticker(chat_id=user_mess_id, sticker=sticker)
                await message.reply(text="Отправлено 🕊")


@dp.message_handler(chat_type=types.ChatType.GROUP, is_reply=True, content_types=types.ContentType.PHOTO)
async def grouppp(message: types.Message):
    user = types.User.get_current().id
    if str(user) in admins:
        if message.chat.id == int(ADMIN_CHAT_ID):
            if message.reply_to_message != None and message.reply_to_message.forward_from != None:
                user_mess_id = message.reply_to_message.forward_from.id
                photo = message.photo[-1].file_id
                text = message.caption

                await bot.send_photo(photo=photo, caption=text, chat_id=user_mess_id)
                await message.reply(text="Отправлено 🕊")


@dp.message_handler(chat_type=types.ChatType.GROUP)
async def group_ignore(message: types.Message):
    pass


@dp.message_handler(commands=["cancel"], state=NewScreenshot)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Отправка фото отменена", reply_markup=ReplyKeyboardRemove())
    await state.reset_state()
    await show_menu(message)


@dp.message_handler(commands=["cancel"], state=WriteToAdmins.Text)
async def cancel_write(message: types.Message, state: FSMContext):
    await state.reset_state()
    await show_menu(message)

@dp.message_handler(commands=["menu"], state=WriteToAdmins.Text)
async def cancel_write(message: types.Message, state: FSMContext):
    await state.reset_state()
    await show_menu(message)


@dp.message_handler(Command("send_photo"))
async def send_photo_choose_test(message: Union[types.Message, types.CallbackQuery]):
    text = "➡ Выбери тему мудла.\nЕсли твоей темы нет в списке нажми кнопку 'Новая тема'"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    tests = await get_tests()
    for test in tests:
        keyboard.add(test.test_name)
    keyboard.add("Новая тема")
    if type(message) == types.Message:
        await message.answer(text=text, reply_markup=keyboard)
    else:
        try:
            await message.message.delete()
        except:
            pass
        await message.message.answer(text=text, reply_markup=keyboard)
    await NewScreenshot.Test.set()


@dp.message_handler(state=NewScreenshot.Test)
async def send_photo_choose_exercise(message: types.Message, state: FSMContext):
    test_name = message.text
    if (test_name == "Новая тема"):
        await message.answer(text="Пришли мне название темы")
        return
    screenshot = Screenshots()
    screenshot.test_name = test_name
    test_code = await get_test_code(test_name)
    screenshot.test_code = test_code
    text = "➡ Выбери номер задания.\nЕсли такого номера нет в списке нажми кнопку 'Новый номер'"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    exercises = await get_exercise(test_code)
    listOfStr = []
    listOfInt = [[], [], []]
    for i in range(len(exercises)):
        if exercises[i].exercise_name.isdigit():
            count = 0
            for j in exercises[i].exercise_name:
                count += 1
            listOfInt[count].append(exercises[i])
        else:
            listOfStr.append(exercises[i])
    listOfInt[0].sort(key=lambda x: x.exercise_name)
    listOfInt[1].sort(key=lambda x: x.exercise_name)
    listOfInt[2].sort(key=lambda x: x.exercise_name)
    listOfStr.sort(key=lambda x: x.exercise_name)
    exercises = listOfInt[0] + listOfInt[1] + listOfInt[2] + listOfStr
    for exercise in exercises:
        keyboard.add(exercise.exercise_name)
    keyboard.add("Новый номер")
    await message.answer(text=text, reply_markup=keyboard)
    await NewScreenshot.Exercise.set()
    await state.update_data(screenshot=screenshot)


@dp.message_handler(state=NewScreenshot.Exercise)
async def send_photo_choose_photo(message: types.Message, state: FSMContext):
    exercise_name = message.text
    if (exercise_name == "Новый номер"):
        await message.answer(text="➡ Пришли мне номер задания")
        return
    data = await state.get_data()
    screenshot: Screenshots = data.get("screenshot")
    screenshot.exercise_name = exercise_name
    exercise_code = await get_exercise_code(exercise_name, screenshot.test_code)
    screenshot.exercise_code = exercise_code
    text = "➡ Пришли свой скриншот задания\nВыше пример идеального скриншота, за который ты получишь максимальный бал (на нем видно всё задание полностью, виден бал за задание и галочка. Но нет ничего лишнего)\n➡ Чтобы отменить отправку своего фото нажмите /cancel"
    await message.answer_photo(caption=text, reply_markup=ReplyKeyboardRemove(),
                               photo="AgACAgIAAxkBAAIT9GBc0avtGDmDknyTaGvZP7G9lIWqAAI8sjEbR9nhSjJ6XryWWI0W6ZOboi4AAwEAAwIAA3gAAxQ5AAIeBA")
    await NewScreenshot.Photo.set()
    await state.update_data(screenshot=screenshot)


@dp.message_handler(state=NewScreenshot.Photo, content_types=types.ContentType.PHOTO)
async def send_photo_confirm(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    screenshot: Screenshots = data.get("screenshot")
    screenshot.photo = photo
    screenshot.isCheck = False
    user = types.User.get_current().id
    if str(user) in admins:
        screenshot.isCheck = True
    text = "Тема: {test}\nНомер задания: {exercise}".format(test=screenshot.test_name,
                                                            exercise=screenshot.exercise_name)
    markup = InlineKeyboardMarkup(inline_keyboard=
    [
        [InlineKeyboardButton(text="Да", callback_data="confirm")],
        [InlineKeyboardButton(text="Неправильная тема", callback_data="change_test")],
        [InlineKeyboardButton(text="Неправильный номер задания", callback_data="change_exercise")],
        [InlineKeyboardButton(text="Неправильное фото", callback_data="change_photo")]
    ])

    await message.answer_photo(caption=text, photo=photo)
    await message.answer(text="Все верно?", reply_markup=markup)
    await NewScreenshot.Confirm.set()
    await state.update_data(screenshot=screenshot)


@dp.message_handler(state=NewScreenshot.ChangeTest)
async def send_photo_confirm_test(message: types.Message, state: FSMContext):
    test = message.text
    if (test == "Новая тема"):
        await message.answer(text="Пришли мне название темы")
        return
    data = await state.get_data()
    screenshot: Screenshots = data.get("screenshot")
    screenshot.test_name = test
    screenshot.test_code = await get_test_code(test)
    screenshot.exercise_code = await get_exercise_code(exercise_name=screenshot.exercise_name,
                                                       test_code=screenshot.test_code)
    text = "Тема: {test}\nНомер задания: {exercise}".format(test=screenshot.test_name,
                                                            exercise=screenshot.exercise_name)
    markup = InlineKeyboardMarkup(inline_keyboard=
    [
        [InlineKeyboardButton(text="Да", callback_data="confirm")],
        [InlineKeyboardButton(text="Неправильная тема", callback_data="change_test")],
        [InlineKeyboardButton(text="Неправильный номер задания", callback_data="change_exercise")],
        [InlineKeyboardButton(text="Неправильное фото", callback_data="change_photo")]
    ])

    await message.answer_photo(caption=text, photo=screenshot.photo, reply_markup=ReplyKeyboardRemove())
    await message.answer(text="Все верно?", reply_markup=markup)
    await NewScreenshot.Confirm.set()
    await state.update_data(screenshot=screenshot)


@dp.message_handler(state=NewScreenshot.ChangeExercise)
async def send_photo_confirm_exercise(message: types.Message, state: FSMContext):
    exercise = message.text
    if (exercise == "Новый номер"):
        await message.answer(text="Пришли мне номер задания")
        return
    data = await state.get_data()
    screenshot: Screenshots = data.get("screenshot")
    screenshot.exercise_name = exercise
    screenshot.exercise_code = await get_exercise_code(exercise, screenshot.test_code)
    text = "Тема: {test}\nНомер задания: {exercise}".format(test=screenshot.test_name,
                                                            exercise=screenshot.exercise_name)
    markup = InlineKeyboardMarkup(inline_keyboard=
    [
        [InlineKeyboardButton(text="Да", callback_data="confirm")],
        [InlineKeyboardButton(text="Неправильная тема", callback_data="change_test")],
        [InlineKeyboardButton(text="Неправильный номер задания", callback_data="change_exercise")],
        [InlineKeyboardButton(text="Неправильное фото", callback_data="change_photo")]
    ])

    await message.answer_photo(caption=text, photo=screenshot.photo, reply_markup=ReplyKeyboardRemove())
    await message.answer(text="Все верно?", reply_markup=markup)
    await NewScreenshot.Confirm.set()
    await state.update_data(screenshot=screenshot)


@dp.callback_query_handler(state=NewScreenshot.Confirm, text_contains="confirm")
async def send_photo_exit(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
    except:
        pass
    data = await state.get_data()
    screenshot: Screenshots = data.get("screenshot")
    screenshot.author = types.User.get_current().id
    screenshot.isDeleted = False
    await screenshot.create()
    await call.message.answer_sticker(sticker="CAACAgQAAxkBAAIGY1__bX4guaYl8QWzRpvQHgju0EHRAAJ9AAPOOQgNKBlAtyUPuOIeBA")
    if not str(call.message.chat.id) in admins:
        text = "😍 Спасибо, скриншот отправлен админам. Ожидай награду..."
    else:
        text = "Ваш скриншот сохранен. Спасибо. Монетки тебе прийдут... какие монетки дядя, ты ж админ, алле)"
    markup = InlineKeyboardMarkup(inline_keyboard=
    [
        [InlineKeyboardButton(text="Отправить скриншот другого заданиия", callback_data="new_exercise")],
        [InlineKeyboardButton(text="Главное меню", callback_data="to_menu")],
    ])
    await call.message.answer(text=text, reply_markup=markup)
    size = len(await get_unchaked_screenshots())
    if not str(call.message.chat.id) in admins:
        for admin in admins:
            await bot.send_message(chat_id=admin, text="В предложке скринов: "+str(size)+" 📥")


@dp.callback_query_handler(text_contains="new_exercise", state=NewScreenshot.Confirm)
async def send_photo_new_exercise(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    data = await state.get_data()
    screenshot: Screenshots = data.get("screenshot")
    text = "➡ Выбери номер задания.\nЕсли такого номера нет в списке нажми кнопку 'Новый номер'"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    exercises = await get_exercise(screenshot.test_code)
    listOfStr = []
    listOfInt = [[], [], []]
    for i in range(len(exercises)):
        if exercises[i].exercise_name.isdigit():
            count = 0
            for j in exercises[i].exercise_name:
                count += 1
            listOfInt[count].append(exercises[i])
        else:
            listOfStr.append(exercises[i])
    listOfInt[0].sort(key=lambda x: x.exercise_name)
    listOfInt[1].sort(key=lambda x: x.exercise_name)
    listOfInt[2].sort(key=lambda x: x.exercise_name)
    listOfStr.sort(key=lambda x: x.exercise_name)
    exercises2 = listOfInt[0] + listOfInt[1] + listOfInt[2] + listOfStr
    for exercise in exercises2:
        keyboard.add(exercise.exercise_name)
    keyboard.add("Новый номер")
    await call.message.answer(text=text, reply_markup=keyboard)
    await NewScreenshot.Exercise.set()


@dp.callback_query_handler(text_contains="to_menu", state=NewScreenshot.Confirm)
async def send_photo_to_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await state.reset_state()
    await show_menu(call.message)


@dp.callback_query_handler(text_contains="change_test", state=NewScreenshot.Confirm)
async def send_photo_change_test(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
    except:
        pass
    text = "➡ Выбери тему мудла.\nЕсли твоей темы нет в списке нажми кнопку 'Новая тема'"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    tests = await get_tests()
    for test in tests:
        keyboard.add(test.test_name)
    keyboard.add("Новая тема")
    await call.message.answer(text=text, reply_markup=keyboard)
    await NewScreenshot.ChangeTest.set()


@dp.callback_query_handler(text_contains="change_exercise", state=NewScreenshot.Confirm)
async def send_photo_change_exercise(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
    except:
        pass
    data = await state.get_data()
    screenshot: Screenshots = data.get("screenshot")
    test_code = screenshot.test_code
    text = "➡ Выбери номер задания.\nЕсли такого номера нет в списке нажми кнопку 'Новый номер'"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    exercises = await get_exercise(test_code)
    listOfStr = []
    listOfInt = [[], [], []]
    for i in range(len(exercises)):
        if exercises[i].exercise_name.isdigit():
            count = 0
            for j in exercises[i].exercise_name:
                count += 1
            listOfInt[count].append(exercises[i])
        else:
            listOfStr.append(exercises[i])
    listOfInt[0].sort(key=lambda x: x.exercise_name)
    listOfInt[1].sort(key=lambda x: x.exercise_name)
    listOfInt[2].sort(key=lambda x: x.exercise_name)
    listOfStr.sort(key=lambda x: x.exercise_name)
    exercises = listOfInt[0] + listOfInt[1] + listOfInt[2] + listOfStr
    for exercise in exercises:
        keyboard.add(exercise.exercise_name)
    keyboard.add("Новый номер")
    await call.message.answer(text=text, reply_markup=keyboard)
    await NewScreenshot.ChangeExercise.set()


@dp.callback_query_handler(text_contains="change_photo", state=NewScreenshot.Confirm)
async def send_photo_change_photo(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
    except:
        pass
    text = "➡ Пришли свой скриншот задания.\n➡ Чтобы отменить отправку своего фото нажми /cancel"
    await call.message.answer(text=text)
    await NewScreenshot.Photo.set()


def send_action():
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action="typing")
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator


@dp.message_handler(Command("referrals"))
async def my_referrals(message: Union[types.Message, types.CallbackQuery]):
    user = types.User.get_current().id
    referrals = await get_referrals(user)
    referral_code = await get_referral_link(user)
    text = "➡ Твоя реферальная ссылка:\n" + referral_code + "\nКогда друг перейдет по твоей ссылке, он получит 50 дополнительных монет.\nТы получишь 50 монет когда твой друг откроет любую тему\n\n"
    if not referrals == []:
        text += "Твои рефералы:\n"
        for num, row in enumerate(referrals):
            text += str(num + 1) + ') <a href="tg://user?id=' + str(row.tg_id) + '">' + row.full_name + '</a>\n'
    else:
        text += "У тебя пока нет рефералов"
    if type(message) == types.Message:
        await message.answer(text)
    else:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.row(InlineKeyboardButton(text="Назад", callback_data=make_callback_data(level=2, menu_type="2")))
        await message.message.edit_text(text=text, reply_markup=markup)


@dp.message_handler(Command("balance"))
async def my_balance(message: Union[types.Message, types.CallbackQuery]):
    user = types.User.get_current().id
    balance = await check_money(user)
    text = "На твоем счету " + balance + " монет."
    if type(message) == types.Message:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.row(
            InlineKeyboardButton(text="Заработать монеты 💰", callback_data=make_callback_data(level=2, menu_type="2")))
        await message.answer(text=text, reply_markup=markup)
    else:
        markup = InlineKeyboardMarkup(row_width=1)
        markup.row(
            InlineKeyboardButton(text="Заработать монеты 💰", callback_data=make_callback_data(level=2, menu_type="2")))
        markup.row(InlineKeyboardButton(text="« Назад", callback_data=make_callback_data(level=0, menu_type="1")))
        await message.message.edit_text(text=text, reply_markup=markup)


@dp.message_handler(Command("menu"))
async def show_menu(message: types.Message):
    await list_first(message)


async def list_first(message: Union[types.Message, types.CallbackQuery], **kwargs):
    markup = await first_keyboard()
    if isinstance(message, types.Message):
        first_name = message['from']['first_name']
        await message.answer("Рады тебя видеть, " + first_name + " ✨", reply_markup=markup)
    elif isinstance(message, types.CallbackQuery):
        first_name = message.message['from']['first_name']
        await message.message.edit_text("Рады тебя видеть, " + first_name + " ✨", reply_markup=markup)



async def list_first_new(message: Union[types.Message, types.CallbackQuery], **kwargs):
    markup = await first_keyboard()
    #await bot.send_message(393483876,str(message))
    if isinstance(message, types.Message):
        first_name = message['chat']['first_name']
        await message.answer("Рады тебя видеть, " + first_name + " ✨", reply_markup=markup)
    elif isinstance(message, types.CallbackQuery):
        first_name = message.message['chat']['first_name']
        await message.message.delete()
        await message.message.answer("Рады тебя видеть, " + first_name + " ✨", reply_markup=markup)


async def list_earns(callback: types.CallbackQuery, **kwargs):
    markup = await earn_keyboard()
    user = types.User.get_current().id
    balance = await check_money(user)
    text = "На твоем счету " + await vidminok(balance)+" 💰\n\n➡ Заработать монеты можно двумя способами:"
    await callback.message.edit_text(text, reply_markup=markup)


async def list_tests(callback: types.CallbackQuery, **kwargs):
    markup = await tests_keyboard()
    user = types.User.get_current().id
    balance = await check_money(user)
    text = "На твоем счету " + await vidminok(balance)+" 💰\n\n➡ Все доступные темы тестов:"
    await callback.message.edit_text(text, reply_markup=markup)


async def not_enaugh_money(callback: types.CallbackQuery, money):
    markup = await not_enough_money_keyboard()
    text = "К сожалению тебе не хватает " + str(money) + " монет, чтоб открыть этот курс 😩"
    await callback.message.edit_text(reply_markup=markup, text=text)


async def is_enaugh_to_enter(callback: types.CallbackQuery, test, i, **kwargs):
    user_id = types.User.get_current().id
    user = await get_user(user_id)
    balance = int(user.balance)
    if balance < int(i):
        await not_enaugh_money(callback, int(i) - balance)
    else:
        await confirm_entrance(callback, test, int(i))


async def confirm_entrance(callback: types.CallbackQuery, test, i, **kwargs):
    markup = await confirm_entrance_keyboard(test, i)
    test_name = await get_test_name(test)
    text = "Ты уверен, что хочешь открыть тему " + test_name + "?\nС твоего счета спишется <b><u>" + str(
        i) + " монет</u></b> 💵\n<b>Скриншоты будут доступны 3 часа, так что открывайте их только когда пишете тест</b>"
    await callback.message.edit_text(reply_markup=markup, text=text)


async def confirm_exit(callback: types.CallbackQuery, test, exercise, i, **kwargs):
    markup = await confirm_exit_keyboard(test=test, exercise=exercise, i=i)
    test_name = await get_test_name(test)
    media = types.InputMediaPhoto(
        "AgACAgIAAxkBAAJKrmByIJ7uUzLtJy0GtS1OWu0efID6AAJGsjEbB3aRSwEl7Fosv9oSI4eHnS4AAwEAAwIAA3kAAzHyAAIeBA")
    text = "⁉ Ты уверен, что хочешь закрыть тему " + test_name + "?\n<b>Вернуться обратно можно будет только платно</b>"
    await callback.message.edit_media(reply_markup=markup, media=media)


async def referal_send_message_about_activation(user_id):
    user = await get_user(user_id)
    referal = user.referal
    text = '💵 Твой друг <a href="tg://user?id=' + str(
        user_id) + '">' + user.full_name + '</a> воспользовался твоей реферальной ссылкой. За это ты получаешь 50 монет. Ты можешь приглашать столько друзей - сколько захочешь.'
    await change_money(money=50, user_id=referal)
    await bot.send_message(chat_id=referal, text=text)


async def list_exercises(callback: types.CallbackQuery, test, money, **kwargs):
    markup = await exercises_keyboard(test)
    user_id = types.User.get_current().id
    await change_money(money, user_id=user_id)
    referal_status = await get_referral_status(user_id=user_id)
    if not referal_status:
        await referal_send_message_about_activation(user_id)
        await activate_referal(user_id=user_id)
    try:
        await callback.message.edit_text("➡ Выбери номер задания:", reply_markup=markup)
    except:
        pass


async def list_exercises_new(callback: types.CallbackQuery, test, **kwargs):
    markup = await exercises_keyboard(test)
    text = "➡ Выбери номер задания:"
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer(reply_markup=markup, text=text)


async def list_screenshots(callback: types.CallbackQuery, test, exercise, i, item_id, money, **kwargs):
    user_id = types.User.get_current().id
    await change_money(money, user_id=user_id)
    referal_status = await get_referral_status(user_id=user_id)
    if not referal_status:
        await referal_send_message_about_activation(user_id)
        await activate_referal(user_id=user_id)
    markup = await screenshots_keyboard(test=test, exercise=exercise, i=i)
    photo = await get_screenshots(test_code=test, exercise_code=exercise)
    try:
        await callback.message.delete()
    except:
        await callback.message.edit_text(text="⤵️")
    new_message = await callback.message.answer_photo(reply_markup=markup, photo=photo[int(i)].photo)
    if item_id == 1:
        await start_timer(message=new_message)


async def list_screenshots_edit(callback: types.CallbackQuery, test, exercise, i, **kwargs):
    markup = await screenshots_keyboard(test=test, exercise=exercise, i=i)
    photo = await get_screenshots(test_code=test, exercise_code=exercise)
    media = types.InputMediaPhoto(photo[int(i)].photo)
    try:
        await callback.message.edit_media(reply_markup=markup, media=media)
    except:
        pass


async def start_timer(message: types.Message):
    await asyncio.sleep(10800)
    try:
        await message.delete()
        await list_first_new(message=message)
    except:
        pass


async def write_to_admins(callback: types.CallbackQuery, **kwargs):
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer(
        text="➡ Все, что ты сейчас пришлешь, получат админы.\nЧто бы закончить - нажми /cancel")
    await WriteToAdmins.Text.set()


@dp.message_handler(state=WriteToAdmins.Text, content_types=types.ContentType.ANY)
async def write_to_admins_second(message: types.Message, state: FSMContext):
    await message.forward(chat_id=ADMIN_CHAT_ID)
    await message.answer(
        "Отправлено 🕊\nМожешь отправить еще одно сообщение или вернуться в меню.\nЧто бы выйти - нажми /cancel")


@dp.callback_query_handler(menu_cd.filter())
async def navigate(call: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get('level')
    menu_type = callback_data.get('menu_type')
    test = callback_data.get('test')
    exercise = callback_data.get('exercise')
    item_id = int(callback_data.get('item_id'))
    i = callback_data.get('i')
    money = callback_data.get('money')

    levels = {
        "0": list_first,
        "1": list_tests,
        "2": is_enaugh_to_enter,
        "3": list_exercises,
        "4": list_screenshots,
    }
    if menu_type == "1":

        current_level_function = levels[current_level]

        await current_level_function(
            call, test=test, exercise=exercise, item_id=item_id, menu_type=menu_type, i=i, money=money
        )
    elif menu_type == "2":
        await list_earns(call, menu_type=menu_type)
    elif menu_type == "4":
        await send_photo_choose_test(call)
    elif menu_type == "5":
        await my_referrals(call)
    elif menu_type == "6":
        await list_screenshots_edit(call, test=test, exercise=exercise, i=i, menu_type=menu_type)
    elif menu_type == "7":
        await list_exercises_new(call, test=test)
    elif menu_type == "8":
        await confirm_exit(call, test=test, exercise=exercise, i=i)
    elif menu_type == "3":
        await my_balance(call)
    elif menu_type == "9":
        await write_to_admins(call)
    elif menu_type == "10":
        await list_first_new(call)