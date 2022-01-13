from typing import Union

from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from data.config import admins, ADMIN_CHAT_ID
from handlers.users.menu_handlers import list_first, list_first_new
from handlers.users.states import *
from keyboards.inline.menu_keyboards import *
from loader import dp, bot
from utils.db_api.db_commands import get_referrals, get_referral_link, get_screenshot, get_screenshots, get_test_name, \
    change_money, get_user, check_money, get_tests, get_exercise, get_test_code, get_exercise_code, get_referral_status, \
    activate_referal, get_unchaked_screenshots, get_users, get_screenshots_all
from utils.db_api.models import Screenshots



@dp.message_handler(commands=["cancel"], state=Check)
async def cancel_check(message: types.Message, state: FSMContext):
    await message.answer("Отправка фото отменена", reply_markup=ReplyKeyboardRemove())
    data = await state.get_data()
    i = data.get("i")
    await state.reset_state()
    if i != None:
        await watch_predlozhka(message=message, i=i)
    else:
        await watch_predlozhka(message=message, i=0)


@dp.message_handler(commands=["cancel"], state=ChangeFromDB)
async def cancel_check(message: types.Message, state: FSMContext):
    data = await state.get_data()
    screenshot: Screenshots = data.get("screenshot")
    i = data.get("i")

    await screenshot.update(isCheck=screenshot.isCheck, test_name=screenshot.test_name, photo=screenshot.photo,
                            exercise_name=screenshot.exercise_name, test_code=screenshot.test_code,
                            exercise_code=screenshot.exercise_code, isDeleted=screenshot.isDeleted,
                            author=screenshot.author).apply()
    author = await get_user(screenshot.author)
    markup = await screen_info_db_keyboard(item_id=screenshot.author, i=i, test=screenshot.test_code,
                                           exercise=screenshot.exercise_code)
    caption = "Тест: " + screenshot.test_name
    caption += "\nЗадание: " + screenshot.exercise_name
    caption += "\nАвтор: " + '<a href="tg://user?id=' + str(author.tg_id) + '">' + str(
        author.full_name) + '</a>'
    caption += "\nId: " + str(screenshot.id)
    caption += "\nПроверен: " + str(screenshot.isCheck)
    caption += "\nУдален: " + str(screenshot.isDeleted)
    caption += "\nКод теста: " + str(screenshot.test_code)
    caption += "\nКод задания: " + str(screenshot.exercise_code)
    caption += "\nКод скрина: " + str(screenshot.photo)
    await message.answer(text="Отмена", reply_markup=ReplyKeyboardRemove())
    await message.answer_photo(caption=caption, photo=screenshot.photo, reply_markup=markup)

    await state.reset_state()


@dp.message_handler(commands=["cancel"], state=WriteToAdmins.ToUser)
async def cancel_write(message: types.Message, state: FSMContext):
    await message.answer("Ты вышел из режима ответов", reply_markup=ReplyKeyboardRemove())
    await state.reset_state()


@dp.message_handler(commands=["cancel"], state=PushAlbom)
async def cancel_push(message: types.Message, state: FSMContext):
    await message.answer("Ты отменил отправку фото", reply_markup=ReplyKeyboardRemove())
    await state.reset_state()
    await list_first(message=message)

@dp.message_handler(commands=["finish"], state=PushAlbom.Photo)
async def cancel(message: types.Message, state: FSMContext):
    user = types.User.get_current().id
    if str(user) in admins:
        markup = await push_album_keyboard()
        await message.answer("Выбери действие", reply_markup=markup)
    await PushAlbom.Confirm.set()


@dp.message_handler(Command("watch_predlozhka"))
async def watch_predlozhka(message: Union[types.Message, types.CallbackQuery], i=0, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        screenshots = await get_unchaked_screenshots()
        if type(message) == types.Message:
            if not screenshots:
                await list_first_new(message)
               # await message.answer(text="Нет непроверенных скриншотов")
            else:
                markup = await unchaked_screenshots_keyboard(screenshots=screenshots, i=i)
                await message.answer_photo(reply_markup=markup, photo=screenshots[int(i)].photo)
        else:
            if not screenshots:
                await bot.answer_callback_query(callback_query_id=message.id, text="Нет непроверенных скриншотов",
                                                show_alert=True)

            else:
                await message.message.delete()
                markup = await unchaked_screenshots_keyboard(screenshots=screenshots, i=i)
                await message.message.answer_photo(reply_markup=markup, photo=screenshots[int(i)].photo)


async def watch_predlozhka_edit(callback: types.CallbackQuery, i, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        screenshots = await get_unchaked_screenshots()
        markup = await unchaked_screenshots_keyboard(screenshots=screenshots, i=i)
        media = types.InputMediaPhoto(screenshots[int(i)].photo)
        await callback.message.edit_media(media=media, reply_markup=markup)


async def choose_money_to_add(callback: types.CallbackQuery, item_id, i, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        #await callback.message.delete_reply_markup()
        markup = await choose_money_to_add_keyboard(item_id, i)
        await callback.message.edit_caption(caption="Выбери сколько монет начислить", reply_markup=markup)


async def choose_money_to_dismiss(callback: types.CallbackQuery, item_id, i, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        #await callback.message.delete_reply_markup()
        markup = await choose_money_to_dismiss_keyboard(item_id, i)
        await callback.message.edit_caption(caption="Выбери сколько монет начислить", reply_markup=markup)


async def choose_what_to_change(callback: types.CallbackQuery, item_id, i, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        await callback.message.delete_reply_markup()
        markup = await edit_photo_from_predlozhka_keyboard(item_id, i)
        screenshot = await get_screenshot(item_id)
        text = "Тема: {test}\nНомер задания: {exercise}\nВыбери что хочешь изменить или нажми /cancel".format(
            test=screenshot.test_name,
            exercise=screenshot.exercise_name)
        await callback.message.answer(text=text, reply_markup=markup)
        await Check.Change.set()


async def confirm_check(callback: types.CallbackQuery, item_id, money, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        screenshot = await get_screenshot(item_id)
        if screenshot.isCheck==True:
            await callback.message.edit_caption(caption="Сорян, походу другой админ уже проверил этот скрин", reply_markup=None)
            await watch_predlozhka(callback.message)
        else:
            await screenshot.update(isCheck=True).apply()
            await change_money(money=money, user_id=screenshot.author)
            balance = await check_money(screenshot.author)
            text_for_author = "Привет! Модератор проверил твой скриншот задания {exercise} по теме '{test}'\nТебе начислено {money} монет, теперь твой балланс {balance} монет" \
                .format(test=screenshot.test_name, exercise=screenshot.exercise_name, money=money, balance=balance)
            await bot.send_message(chat_id=screenshot.author, text=text_for_author)
            #await callback.message.delete_reply_markup()
            try:
                await callback.message.delete()
            except:
                await callback.message.edit_text(text="Готово")
            await watch_predlozhka(callback.message)


async def confirm_dismiss(callback: types.CallbackQuery, item_id, money, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        screenshot = await get_screenshot(item_id)
        if screenshot.isCheck==True:
            await callback.message.edit_caption(caption="Сорян, походу другой админ уже проверил этот скрин", reply_markup=None)
            await watch_predlozhka(callback.message)
        else:
            await screenshot.update(isCheck=True, isDeleted=True).apply()
            await change_money(money=money, user_id=screenshot.author)
            balance = await check_money(screenshot.author)
            text_for_author = "Привет! Модератор проверил твой скриншот задания {exercise} по теме '{test}'\nТебе начислено {money} монет, теперь твой балланс {balance} монет".format(
                test=screenshot.test_name,
                exercise=screenshot.exercise_name, money=money, balance=balance)
            await bot.send_message(chat_id=screenshot.author, text=text_for_author)
            try:
                await callback.message.delete()
            except:
                await callback.message.edit_text(text="Готово")
            await watch_predlozhka(callback.message)


@dp.callback_query_handler(state=Check.Change)
async def change_something_in_checking(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        await callback.message.delete_reply_markup()
        data = callback.data
        data_splited = data.split("_")
        screenshot = await get_screenshot(int(data_splited[2]))
        i=data_splited[3]
        await state.update_data(screenshot=screenshot, i=i)
        if "photo" in data_splited:
            await callback.message.edit_text(text="Пришли другое фото")
            await Check.ChangePhoto.set()
        elif "test" in data_splited:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            tests = await get_tests()
            for test in tests:
                keyboard.add(test.test_name)
            keyboard.add("Новая тема")
            await callback.message.delete()
            text = "Выбери тему мудла.\nЕсли твоей темы нет в списке нажми кнопку 'Новая тема'\nЧтобы отменить отправку своего фото нажмите /cancel"
            await callback.message.answer(text=text, reply_markup=keyboard)
            await Check.ChangeTest.set()
        elif "exercise" in data_splited:
            text = "Выбери номер задания.\nЕсли такого номера нет в списке нажми кнопку 'Новый номер'\nЧтобы отменить отправку своего фото нажмите /cancel"
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            exercises = await get_exercise(screenshot.test_code)
            for exercise in exercises:
                keyboard.add(exercise.exercise_name)
            keyboard.add("Новый номер")
            await callback.message.answer(text=text, reply_markup=keyboard)
            await Check.ChangeExercise.set()


@dp.callback_query_handler(state=PushAlbom.Confirm)
async def change_something_in_checking(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        await callback.message.delete_reply_markup()
        data = callback.data
        data_splited = data.split("_")
        if "exit" in data_splited:
            await callback.message.edit_text(text="Споки Чмоки")
            await state.reset_state()
        elif "test" in data_splited:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            tests = await get_tests()
            for test in tests:
                keyboard.add(test.test_name)
            keyboard.add("Новая тема")
            text = "Выбери тему мудла.\nЕсли твоей темы нет в списке нажми кнопку 'Новая тема'\nЧтобы отменить отправку своего фото нажмите /cancel"
            await callback.message.answer(text=text, reply_markup=keyboard)
            await PushAlbom.Test.set()
        elif "exercise" in data_splited:
            text = "Выбери номер задания.\nЕсли такого номера нет в списке нажми кнопку 'Новый номер'\nЧтобы отменить отправку своего фото нажмите /cancel"
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            data = await state.get_data()
            screenshot = data.get("screenshot")
            exercises = await get_exercise(screenshot.test_code)
            for exercise in exercises:
                keyboard.add(exercise.exercise_name)
            keyboard.add("Новый номер")
            await callback.message.answer(text=text, reply_markup=keyboard)
            await PushAlbom.Exercise.set()


@dp.callback_query_handler(state=Check.ChangeMore)
async def change_something_in_checking(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        await callback.message.delete_reply_markup()
        calldata = callback.data.split("_")
        data = await state.get_data()
        screenshot: Screenshots = data.get("screenshot")
        if "photo" in calldata:
            await callback.message.edit_text(
                text="Пришли другое фото\nЧтобы отменить отправку своего фото нажмите /cancel")
            await Check.ChangePhoto.set()
        elif "test" in calldata:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            tests = await get_tests()
            for test in tests:
                keyboard.add(test.test_name)
            keyboard.add("Новая тема")
            await callback.message.delete()
            text = "Выбери тему мудла.\nЕсли твоей темы нет в списке нажми кнопку 'Новая тема'\nЧтобы отменить отправку своего фото нажмите /cancel"
            await callback.message.answer(text=text, reply_markup=keyboard)
            await Check.ChangeTest.set()
        elif "exercise" in calldata:
            text = "Выбери номер задания.\nЕсли такого номера нет в списке нажми кнопку 'Новый номер'\nЧтобы отменить отправку своего фото нажмите /cancel"
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            exercises = await get_exercise(screenshot.test_code)
            for exercise in exercises:
                keyboard.add(exercise.exercise_name)
            keyboard.add("Новый номер")
            await callback.message.answer(text=text, reply_markup=keyboard)
            await Check.ChangeExercise.set()
        elif "conf" in calldata:
            markup = await choose_money_to_add_keyboard(item_id=screenshot.id, i=data.get("i"))
            await callback.message.answer(text="Выбери сколько монет начислить", reply_markup=markup)
            await screenshot.update(isCheck=True, test_name=screenshot.test_name, photo=screenshot.photo,
                                    exercise_name=screenshot.exercise_name, test_code=screenshot.test_code,
                                    exercise_code=screenshot.exercise_code).apply()

            await state.reset_state()


@dp.message_handler(state=Check.ChangePhoto, content_types=types.ContentType.PHOTO)
async def change_photo_in_checking(message: types.Message, state: FSMContext, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        photo = message.photo[-1].file_id
        data = await state.get_data()
        screenshot: Screenshots = data.get("screenshot")
        screenshot.photo = photo
        text = "Тема: {test}\nНомер задания: {exercise}".format(test=screenshot.test_name,
                                                                exercise=screenshot.exercise_name)
        markup = InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(text="Да", callback_data="change_conf")],
            [InlineKeyboardButton(text="Неправильная тема",
                                  callback_data="change_test_{item_id}".format(item_id=screenshot.id))],
            [InlineKeyboardButton(text="Неправильный номер задания",
                                  callback_data="change_exercise_{item_id}".format(item_id=screenshot.id))],
            [InlineKeyboardButton(text="Неправильное фото",
                                  callback_data="change_photo_{item_id}".format(item_id=screenshot.id))]
        ])
        await message.answer_photo(caption=text, photo=photo)
        await message.answer(text="Все верно?\nНажми /cancel чтоб отменить", reply_markup=markup)
        await Check.ChangeMore.set()
        await state.update_data(screenshot=screenshot)


@dp.message_handler(state=Check.ChangeTest)
async def change_test_in_checking(message: types.Message, state: FSMContext):
    user = types.User.get_current().id
    if str(user) in admins:
        test = message.text
        if (test == "Новая тема"):
            await message.answer(text="Пришли мне название темы или нажми /cancel чтоб отменить")
            return
        data = await state.get_data()
        screenshot: Screenshots = data.get("screenshot")
        screenshot.test_name = test
        screenshot.test_code = await get_test_code(test)
        text = "Тема: {test}\nНомер задания: {exercise}".format(test=screenshot.test_name,
                                                                exercise=screenshot.exercise_name)
        markup = InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(text="Да", callback_data="change_conf")],
            [InlineKeyboardButton(text="Неправильная тема", callback_data="change_test")],
            [InlineKeyboardButton(text="Неправильный номер задания", callback_data="change_exercise")],
            [InlineKeyboardButton(text="Неправильное фото", callback_data="change_photo")]
        ])

        await message.answer_photo(caption=text, photo=screenshot.photo, reply_markup=ReplyKeyboardRemove())
        await message.answer(text="Все верно?", reply_markup=markup)
        await Check.ChangeMore.set()
        await state.update_data(screenshot=screenshot)


@dp.message_handler(state=Check.ChangeExercise)
async def change_exercise_in_checking(message: types.Message, state: FSMContext):
    user = types.User.get_current().id
    if str(user) in admins:
        exercise = message.text
        if (exercise == "Новый номер"):
            await message.answer(text="Пришли мне номер задания или ажми /cancel чтоб отменить")
            return
        data = await state.get_data()
        screenshot: Screenshots = data.get("screenshot")
        screenshot.exercise_name = exercise
        screenshot.exercise_code = await get_exercise_code(exercise, screenshot.test_code)
        text = "Тема: {test}\nНомер задания: {exercise}".format(test=screenshot.test_name,
                                                                exercise=screenshot.exercise_name)
        markup = InlineKeyboardMarkup(inline_keyboard=
        [
            [InlineKeyboardButton(text="Да", callback_data="change_conf")],
            [InlineKeyboardButton(text="Неправильная тема", callback_data="change_test")],
            [InlineKeyboardButton(text="Неправильный номер задания", callback_data="change_exercise")],
            [InlineKeyboardButton(text="Неправильное фото", callback_data="change_photo")]
        ])

        await message.answer_photo(caption=text, photo=screenshot.photo, reply_markup=ReplyKeyboardRemove())
        await message.answer(text="Все верно?", reply_markup=markup)
        await Check.ChangeMore.set()
        await state.update_data(screenshot=screenshot)


async def close_predlozhka(callback: types.CallbackQuery, **kwargs):
    await callback.message.delete()
    await list_first(callback.message)


@dp.message_handler(Command("answer"))
async def reply_to_user_set(message: Union[types.Message, types.CallbackQuery], item_id, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        if type(message) == types.Message:
            await message.answer(text="Ты вошел в режим ответа\nЧтоб выйти из режима ответа нажми /cancel")
        else:
            await message.message.delete()
            await message.message.answer(text="Ты вошел в режим ответа\nЧтоб выйти из режима ответа нажми /cancel")
        await WriteToAdmins.ToUser.set()


@dp.message_handler(Command("push_album"))
async def push_album(message: Union[types.Message, types.CallbackQuery], **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        text="Ты в режиме отправки сразу нескольких фото\nЧтоб выйти из режима нажми /cancel\nСейчас выбери тему теста"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        tests = await get_tests()
        for test in tests:
            keyboard.add(test.test_name)
        keyboard.add("Новая тема")
        if type(message) == types.Message:
            await message.answer(text=text, reply_markup=keyboard)
        else:
            await message.message.delete()
            await message.message.answer(text=text, reply_markup=keyboard)
        await PushAlbom.Test.set()



@dp.message_handler(state=PushAlbom.Test)
async def push_album_test(message: types.Message, state: FSMContext,  **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        test_name = message.text
        if (test_name == "Новая тема"):
            await message.answer(text="Пришли мне название темы или нажми /cancel чтоб отменить")
            return
        screenshot = Screenshots()
        screenshot.test_name = test_name
        test_code = await get_test_code(test_name)
        screenshot.test_code = test_code
        text = "Выбери номер задания.\nЕсли такого номера нет в списке нажми кнопку 'Новый номер'\nЧтобы отменить отправку своего фото нажмите /cancel"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        exercises = await get_exercise(test_code)
        for exercise in exercises:
            keyboard.add(exercise.exercise_name)
        keyboard.add("Новый номер")
        await message.answer(text=text, reply_markup=keyboard)
        await PushAlbom.Exercise.set()
        await state.update_data(screenshot=screenshot)


@dp.message_handler(state=PushAlbom.Exercise)
async def push_album_exercise(message: types.Message, state: FSMContext, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        exercise_name = message.text
        if (exercise_name == "Новый номер"):
            await message.answer(text="Пришли мне номер задания")
            return
        data = await state.get_data()
        screenshot: Screenshots = data.get("screenshot")
        screenshot.exercise_name = exercise_name
        exercise_code = await get_exercise_code(exercise_name, screenshot.test_code)
        screenshot.exercise_code = exercise_code
        text = "Пришли свой скриншот задания.\nЧтобы отменить отправку своего фото нажмите /cancel\nТема: {test}, номер задания: {exercise}".format(test=screenshot.test_name, exercise=screenshot.exercise_name)
        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
        await PushAlbom.Photo.set()
        await state.update_data(screenshot=screenshot)


@dp.message_handler(state=PushAlbom.Photo, content_types=types.ContentType.PHOTO)
async def push_album_photo(message: types.Message, state: FSMContext, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        photo = message.photo[-1].file_id
        data = await state.get_data()
        screenshot: Screenshots = data.get("screenshot")
        screenshot.photo = photo
        screenshot.author = user
        screenshot.isDeleted = False
        screenshot.isCheck = True
        await screenshot.create()
        text = "Отлично, скриншот записан. Пришли другое фото этой темы и задания или нажми /finish\n" \
               "Чтобы отменить отправку своего фото нажмите /cancel\n" \
               "Тема: {test}, номер задания: {exercise}".format(test=screenshot.test_name,
                                                                exercise=screenshot.exercise_name)
        await message.answer(text=text)


@dp.message_handler(state=WriteToAdmins.ToUser, content_types=types.ContentType.TEXT)
async def reply_to_user(message: types.Message, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        if message.reply_to_message != None and message.reply_to_message.forward_from != None:
            user_mess_id = message.reply_to_message.forward_from.id
            await bot.send_message(chat_id=user_mess_id, text=message.text, reply_to_message_id=message.reply_to_message.forward_from_message_id)
            await message.reply(text="Отправлено 🕊\nМожешь продолжать отвечать либо нажать /cancel, чтоб выйти")
        else:
            await message.reply(
                text="Ошибка. Чтоб ответить человеку - напиши текст в с реплаем на его сообщение\nЧтоб выйти из режима ответа нажми /cancel")


@dp.message_handler(state=WriteToAdmins.ToUser, content_types=types.ContentType.STICKER)
async def reply_to_user(message: types.Message, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        if message.reply_to_message != None and message.reply_to_message.forward_from != None:
            user_mess_id = message.reply_to_message.forward_from.id
            sticker = message.sticker.file_id
            await bot.send_sticker(chat_id=user_mess_id, sticker=sticker)
            await message.reply(text="Отправлено 🕊\nЧтоб выйти из режима ответа нажми /cancel")

@dp.message_handler(state=WriteToAdmins.ToUser, content_types=types.ContentType.PHOTO)
async def reply_to_user(message: types.Message, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        if message.reply_to_message is not None and message.reply_to_message.forward_from is not None:
            user_mess_id = message.reply_to_message.forward_from.id
            photo = message.photo[-1].file_id
            text = message.caption

            await bot.send_photo(photo=photo, caption=text, chat_id=user_mess_id)
            await message.reply(text="Отправлено 🕊\nЧтоб выйти из режима ответа нажми /cancel")



async def db_users_list(message: Union[types.Message, types.CallbackQuery], i=0, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:

        if type(message) == types.Message:

            markup = await users_list_keyboard(i)
            await message.answer(reply_markup=markup, text="База юзеров:")
        else:
            markup = await users_list_keyboard(i)
            await message.message.edit_text(reply_markup=markup, text="База юзеров:")


async def db_screens_list(message: Union[types.Message, types.CallbackQuery], i=0, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        markup = await tests_keyboard_db()
        if type(message) == types.Message:


            await message.answer(reply_markup=markup, text="База скриншотов:")
        else:
            try:
                await message.message.edit_text(reply_markup=markup, text="База скриншотов:")
            except:
                await message.message.delete()
                await message.message.answer(reply_markup=markup, text="База скриншотов:")



async def db_users_info(message: Union[types.Message, types.CallbackQuery], item_id=0, i=0, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        user_db = await get_user(user_id=item_id)
        text = '<a href="tg://user?id=' + str(user_db.tg_id) + '">' + str(user_db.full_name) + '</a>\n\n'
        if user_db.username != None:
            text += 'username: @' + user_db.username + '\n'
        else:
            text += 'no username\n'
        text += 'balance: ' + user_db.balance
        if user_db.referal!=None:
            referal = await get_user(user_db.referal)
            text += '\nreferal: ' + '<a href="tg://user?id=' + str(
                referal.tg_id) + '">' + str(referal.full_name) + '</a>\n'
        else:
            text+='\nno referal\n'
        text +="referal code: " + user_db.referal_code + "\ntelegram id: " + str(user_db.tg_id) + "\nis referal activated: " + str(user_db.isReferalActivated) + "\nid: " + str(user_db.id)
        markup = await users_info_keyboard(i=i, item_id=item_id)
        if type(message) == types.Message:

            await message.answer(reply_markup=markup, text=text, disable_web_page_preview=True)
        else:
            try:
                await message.message.edit_text(reply_markup=markup, text=text, disable_web_page_preview=True)
            except:
                await message.message.delete()
                await message.message.answer(reply_markup=markup, text=text, disable_web_page_preview=True)


async def db_users_info_from_screenshot(message: Union[types.Message, types.CallbackQuery], item_id=0, i=0, test=0, exercise=0, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        user_db = await get_user(user_id=item_id)
        text = '<a href="tg://user?id=' + str(user_db.tg_id) + '">' + str(user_db.full_name) + '</a>\n\n'
        if user_db.username != None:
            text += 'username: @' + user_db.username + '\n'
        else:
            text += 'no username\n'
        text += 'balance: ' + user_db.balance
        if user_db.referal!=None:
            referal = await get_user(user_db.referal)
            text += '\nreferal: ' + '<a href="tg://user?id=' + str(
                referal.tg_id) + '">' + str(referal.full_name) + '</a>\n'
        else:
            text+='\nno referal\n'
        text +="referal code: " + user_db.referal_code + "\ntelegram id: " + str(user_db.tg_id) + "\nis referal activated: " + str(user_db.isReferalActivated) + "\nid: " + str(user_db.id)
        markup = await users_info_keyboard_from_screenshot(i=i, test=test, exercise=exercise)
        if type(message) == types.Message:

            await message.answer(reply_markup=markup, text=text, disable_web_page_preview=True)
        else:
            try:
                await message.message.edit_text(reply_markup=markup, text=text, disable_web_page_preview=True)
            except:
                await message.message.delete()
                await message.message.answer(reply_markup=markup, text=text, disable_web_page_preview=True)


async def db_screens_info(callback: types.CallbackQuery, test, exercise, i, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        markup = await screenshots_keyboard_db(test=test, exercise=exercise, i=i)
        photos = await get_screenshots_all(test_code=test, exercise_code=exercise)

        photo=photos[int(i)].photo
        await callback.message.delete()
        await callback.message.answer_photo(reply_markup=markup, photo=photo)

async def db_screens_info_edit(callback: types.CallbackQuery, test, exercise, i, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        markup = await screenshots_keyboard_db(test=test, exercise=exercise, i=i)
        photos = await get_screenshots_all(test_code=test, exercise_code=exercise)
        media = types.InputMediaPhoto(photos[int(i)].photo)
        await callback.message.edit_media(reply_markup=markup, media=media)




async def db_screen_info(callback: types.CallbackQuery, test, exercise, i, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        photos = await get_screenshots_all(test_code=test, exercise_code=exercise)
        markup = await screen_info_db_keyboard(test=test, exercise=exercise, i=i, item_id=photos[int(i)].author)
        photo=photos[int(i)].photo
        author = await get_user(photos[int(i)].author)
        caption = "Тест: " +photos[int(i)].test_name
        caption+= "\nЗадание: "+photos[int(i)].exercise_name
        caption += "\nАвтор: " +'<a href="tg://user?id=' + str(author.tg_id) + '">' + str(author.full_name) + '</a>'
        caption += "\nId: " +str(photos[int(i)].id)
        caption += "\nПроверен: " +str(photos[int(i)].isCheck)
        caption += "\nУдален: " +str(photos[int(i)].isDeleted)
        caption += "\nКод теста: " +str(photos[int(i)].test_code)
        caption += "\nКод задания: " +str(photos[int(i)].exercise_code)
        caption += "\nКод скрина: " +str(photos[int(i)].photo)
        #await callback.message.delete()
        #await callback.message.answer_photo(reply_markup=markup, photo=photo, caption=caption)
        try:
            await callback.message.edit_caption(reply_markup=markup, caption=caption)
        except:
            await callback.message.delete()
            await callback.message.answer_photo(reply_markup=markup, photo=photo, caption=caption)

async def choose_what_to_change_from_db(callback: types.CallbackQuery, i, exercise, test, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:

        markup = await edit_photo_from_db_keyboard(exercise=exercise, i=i, test=test)
        await callback.message.edit_reply_markup(reply_markup=markup)
        await ChangeFromDB.Change.set()


@dp.callback_query_handler(state=ChangeFromDB.Change)
async def change_something_in_checking(callback: types.CallbackQuery, state: FSMContext, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        calldata = callback.data.split("_")
        screenshot = await get_screenshot(int(calldata[1]))
        await state.update_data(screenshot=screenshot)
        await state.update_data(i=calldata[2])
        if "photo" in calldata:
            await callback.message.delete()
            await callback.message.answer(
                text="Пришли другое фото\nЧтобы отменить отправку своего фото нажмите /cancel")
            await ChangeFromDB.ChangePhoto.set()
        elif "test" in calldata:
            await callback.message.delete()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            tests = await get_tests()
            for test in tests:
                keyboard.add(test.test_name)
            keyboard.add("Новая тема")
            text = "Выбери тему мудла.\nЕсли твоей темы нет в списке нажми кнопку 'Новая тема'\nЧтобы отменить отправку своего фото нажмите /cancel"
            await callback.message.answer(text=text, reply_markup=keyboard)
            await ChangeFromDB.ChangeTest.set()
        elif "exercise" in calldata:
            await callback.message.delete()
            text = "Выбери номер задания.\nЕсли такого номера нет в списке нажми кнопку 'Новый номер'\nЧтобы отменить отправку своего фото нажмите /cancel"
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            exercises = await get_exercise(screenshot.test_code)
            for exercise in exercises:
                keyboard.add(exercise.exercise_name)
            keyboard.add("Новый номер")
            await callback.message.answer(text=text, reply_markup=keyboard)
            await ChangeFromDB.ChangeExercise.set()

        elif "delete" in calldata:
            if screenshot.isDeleted:
                await screenshot.update(isCheck=screenshot.isCheck, test_name=screenshot.test_name, photo=screenshot.photo,
                                        exercise_name=screenshot.exercise_name, test_code=screenshot.test_code,
                                        exercise_code=screenshot.exercise_code, isDeleted=False, author=screenshot.author).apply()
                screenshot.isDeleted = False
            else:
                await screenshot.update(isCheck=screenshot.isCheck, test_name=screenshot.test_name, photo=screenshot.photo,
                                        exercise_name=screenshot.exercise_name, test_code=screenshot.test_code,
                                        exercise_code=screenshot.exercise_code, isDeleted=True, author=screenshot.author).apply()
                screenshot.isDeleted = True
            author = await get_user(screenshot.author)
            markup = await screen_info_db_keyboard(item_id=screenshot.author, i=calldata[2], test=screenshot.test_code, exercise=screenshot.exercise_code)
            caption = "Тест: " + screenshot.test_name
            caption += "\nЗадание: " + screenshot.exercise_name
            caption += "\nАвтор: " + '<a href="tg://user?id=' + str(author.tg_id) + '">' + str(
                author.full_name) + '</a>'
            caption += "\nId: " + str(screenshot.id)
            caption += "\nПроверен: " + str(screenshot.isCheck)
            caption += "\nУдален: " + str(screenshot.isDeleted)
            caption += "\nКод теста: " + str(screenshot.test_code)
            caption += "\nКод задания: " + str(screenshot.exercise_code)
            caption += "\nКод скрина: " + str(screenshot.photo)

            await callback.message.edit_caption(caption=caption, reply_markup=markup)
            await state.reset_state()
        elif "return" in calldata:
            author = await get_user(screenshot.author)
            markup = await screen_info_db_keyboard(item_id=screenshot.author, i=calldata[2], test=screenshot.test_code,
                                                   exercise=screenshot.exercise_code)
            caption = "Тест: " + screenshot.test_name
            caption += "\nЗадание: " + screenshot.exercise_name
            caption += "\nАвтор: " + '<a href="tg://user?id=' + str(author.tg_id) + '">' + str(
                author.full_name) + '</a>'
            caption += "\nId: " + str(screenshot.id)
            caption += "\nПроверен: " + str(screenshot.isCheck)
            caption += "\nУдален: " + str(screenshot.isDeleted)
            caption += "\nКод теста: " + str(screenshot.test_code)
            caption += "\nКод задания: " + str(screenshot.exercise_code)
            caption += "\nКод скрина: " + str(screenshot.photo)

            await callback.message.edit_caption(caption=caption, reply_markup=markup)
            await state.reset_state()


@dp.message_handler(state=ChangeFromDB.ChangePhoto, content_types=types.ContentType.PHOTO)
async def change_photo_from_db(message: types.Message, state: FSMContext, **kwargs):
    user = types.User.get_current().id
    if str(user) in admins:
        photo = message.photo[-1].file_id
        data = await state.get_data()
        screenshot: Screenshots = data.get("screenshot")
        i = data.get("i")
        screenshot.photo = photo
        await screenshot.update(isCheck=screenshot.isCheck, test_name=screenshot.test_name, photo=screenshot.photo,
                                exercise_name=screenshot.exercise_name, test_code=screenshot.test_code,
                                exercise_code=screenshot.exercise_code, isDeleted=screenshot.isDeleted,
                                author=screenshot.author).apply()
        author = await get_user(screenshot.author)
        markup = await screen_info_db_keyboard(item_id=screenshot.author, i=i, test=screenshot.test_code,
                                               exercise=screenshot.exercise_code)
        caption = "Тест: " + screenshot.test_name
        caption += "\nЗадание: " + screenshot.exercise_name
        caption += "\nАвтор: " + '<a href="tg://user?id=' + str(author.tg_id) + '">' + str(
            author.full_name) + '</a>'
        caption += "\nId: " + str(screenshot.id)
        caption += "\nПроверен: " + str(screenshot.isCheck)
        caption += "\nУдален: " + str(screenshot.isDeleted)
        caption += "\nКод теста: " + str(screenshot.test_code)
        caption += "\nКод задания: " + str(screenshot.exercise_code)
        caption += "\nКод скрина: " + str(screenshot.photo)
        await message.answer(text="Изменено", reply_markup=ReplyKeyboardRemove())
        await message.answer_photo(caption=caption, photo=photo, reply_markup=markup)

        await state.reset_state()


@dp.message_handler(state=ChangeFromDB.ChangeTest)
async def change_test_in_checking(message: types.Message, state: FSMContext):
    user = types.User.get_current().id
    if str(user) in admins:
        test = message.text
        if (test == "Новая тема"):
            await message.answer(text="Пришли мне название темы или нажми /cancel чтоб отменить")
            return
        data = await state.get_data()
        screenshot: Screenshots = data.get("screenshot")
        i = data.get("i")
        screenshot.test_name = test
        screenshot.test_code = await get_test_code(test)
        screenshot.exercise_code = await get_exercise_code(exercise_name=screenshot.exercise_name, test_code=screenshot.test_code)

        await screenshot.update(isCheck=screenshot.isCheck, test_name=screenshot.test_name, photo=screenshot.photo,
                                exercise_name=screenshot.exercise_name, test_code=screenshot.test_code,
                                exercise_code=screenshot.exercise_code, isDeleted=screenshot.isDeleted,
                                author=screenshot.author).apply()
        author = await get_user(screenshot.author)
        markup = await screen_info_db_keyboard(item_id=screenshot.author, i=i, test=screenshot.test_code,
                                               exercise=screenshot.exercise_code)
        caption = "Тест: " + screenshot.test_name
        caption += "\nЗадание: " + screenshot.exercise_name
        caption += "\nАвтор: " + '<a href="tg://user?id=' + str(author.tg_id) + '">' + str(
            author.full_name) + '</a>'
        caption += "\nId: " + str(screenshot.id)
        caption += "\nПроверен: " + str(screenshot.isCheck)
        caption += "\nУдален: " + str(screenshot.isDeleted)
        caption += "\nКод теста: " + str(screenshot.test_code)
        caption += "\nКод задания: " + str(screenshot.exercise_code)
        caption += "\nКод скрина: " + str(screenshot.photo)
        await message.answer(text="Изменено", reply_markup=ReplyKeyboardRemove())
        await message.answer_photo(caption=caption, photo=screenshot.photo, reply_markup=markup)

        await state.reset_state()


@dp.message_handler(state=ChangeFromDB.ChangeExercise)
async def change_exercise_in_checking(message: types.Message, state: FSMContext):
    user = types.User.get_current().id
    if str(user) in admins:
        exercise = message.text
        if (exercise == "Новый номер"):
            await message.answer(text="Пришли мне номер задания или ажми /cancel чтоб отменить")
            return
        data = await state.get_data()
        screenshot: Screenshots = data.get("screenshot")
        i = data.get("i")
        screenshot.exercise_name = exercise
        screenshot.exercise_code = await get_exercise_code(exercise, screenshot.test_code)

        await screenshot.update(isCheck=screenshot.isCheck, test_name=screenshot.test_name, photo=screenshot.photo,
                                exercise_name=screenshot.exercise_name, test_code=screenshot.test_code,
                                exercise_code=screenshot.exercise_code, isDeleted=screenshot.isDeleted,
                                author=screenshot.author).apply()
        author = await get_user(screenshot.author)
        markup = await screen_info_db_keyboard(item_id=screenshot.author, i=i, test=screenshot.test_code,
                                               exercise=screenshot.exercise_code)
        caption = "Тест: " + screenshot.test_name
        caption += "\nЗадание: " + screenshot.exercise_name
        caption += "\nАвтор: " + '<a href="tg://user?id=' + str(author.tg_id) + '">' + str(
            author.full_name) + '</a>'
        caption += "\nId: " + str(screenshot.id)
        caption += "\nПроверен: " + str(screenshot.isCheck)
        caption += "\nУдален: " + str(screenshot.isDeleted)
        caption += "\nКод теста: " + str(screenshot.test_code)
        caption += "\nКод задания: " + str(screenshot.exercise_code)
        caption += "\nКод скрина: " + str(screenshot.photo)
        await message.answer(text="Изменено", reply_markup=ReplyKeyboardRemove())
        await message.answer_photo(caption=caption, photo=screenshot.photo, reply_markup=markup)

        await state.reset_state()


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

@dp.callback_query_handler(menu_cd_admin.filter())
async def navigate(call: types.CallbackQuery, callback_data: dict):
    current_level = callback_data.get('level')
    test = callback_data.get('test')
    exercise = callback_data.get('exercise')
    item_id = int(callback_data.get('item_id'))
    i = callback_data.get('i')
    money = callback_data.get('money')

    levels = {
        "-1": close_predlozhka,
        "0": watch_predlozhka,
        "1": watch_predlozhka_edit,
        "2": choose_what_to_change,
        "3": watch_predlozhka,
        "4": choose_money_to_add,
        "5": confirm_check,
        "6": choose_money_to_dismiss,
        "7": confirm_dismiss,
        "8": change_something_in_checking,
        "9": push_album,
        "10": db_users_list,
        "11": db_screens_list,
        "12": db_users_info,
        "13": db_screens_info,
        "14": db_screens_info_edit,
        "15": db_screen_info,
        "16": db_users_info_from_screenshot,
        "17": choose_what_to_change_from_db,

    }
    current_level_function = levels[current_level]
    await current_level_function(
        call, test=test, exercise=exercise, item_id=item_id, i=i, money=money
    )
