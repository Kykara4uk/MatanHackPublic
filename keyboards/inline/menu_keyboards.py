from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from data.config import admins
from utils.db_api.db_commands import get_tests, count_screenshots, get_screenshots, get_exercise, change_money, \
    get_checked_tests, price_of_test, get_users, get_screenshots_all, get_screenshot, get_exercises, get_exercises_all
from aiogram import types
menu_cd = CallbackData("show_menu", "level", "test", "exercise", "item_id", "menu_type", "i", "money")


def make_callback_data(level, test="0", exercise="0", item_id="0", menu_type="0", i=0, money=0):
    return menu_cd.new(level=level, test=test, exercise=exercise, item_id=item_id, menu_type=menu_type, i=i,
                       money=money)


menu_cd_admin = CallbackData("show_menu", "level", "test", "exercise", "item_id", "i", "money")


def make_callback_data_admin(level, test="0", exercise="0", item_id="0", i=0, money=0):
    return menu_cd_admin.new(level=level, test=test, exercise=exercise, item_id=item_id, i=i, money=money)


async def first_keyboard():
    CURRENT_LEVEL = 0
    markup = InlineKeyboardMarkup()
    user = types.User.get_current().id
    if str(user) in admins:
        markup.row(InlineKeyboardButton(text="База юзеров",
                                        callback_data=make_callback_data_admin(level=10)),
                   InlineKeyboardButton(text="База скринов",
                                        callback_data=make_callback_data_admin(level=11)))
        markup.row(InlineKeyboardButton(text="Предложка 📪",
                                        callback_data=make_callback_data_admin(level=0)),
                    InlineKeyboardButton(text="Залить ответы 📩",
                                        callback_data=make_callback_data_admin(level=9)))
    markup.row( InlineKeyboardButton(text="🔍 Паль",
                                    callback_data=make_callback_data(level=CURRENT_LEVEL + 1, menu_type="1")),
                InlineKeyboardButton(text="💰 Заработать ",
                                    callback_data=make_callback_data(level=CURRENT_LEVEL + 1, menu_type="2")),
                InlineKeyboardButton(text="✏ Поддержка",
                                    callback_data=make_callback_data(level=CURRENT_LEVEL + 1, menu_type="9")))
    return markup


async def not_enough_money_keyboard():
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text="Заработать монеты 💰", callback_data=make_callback_data(level=1, menu_type="2")),
               InlineKeyboardButton(text="« Отмена",
                                    callback_data=make_callback_data(level=CURRENT_LEVEL - 1, menu_type="1")))
    return markup


async def earn_keyboard():
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text="Отправить свои ответы ✉",
                                    callback_data=make_callback_data(level=CURRENT_LEVEL + 1, menu_type="4")))
    markup.row(InlineKeyboardButton(text="Пригласить друга 🙋‍♂️",
                                    callback_data=make_callback_data(level=CURRENT_LEVEL + 1, menu_type="5")))
    markup.row(
        InlineKeyboardButton(text="« Отмена", callback_data=make_callback_data(level=CURRENT_LEVEL - 1, menu_type="1")))
    return markup

async def answer_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text="Ответить ✏",
                                    callback_data=make_callback_data_admin(level=10)))
    return markup


async def tests_keyboard():
    CURRENT_LEVEL = 1
    markup = InlineKeyboardMarkup(row_width=1)

    tests = await get_checked_tests()
    for test in tests:
        number_of_items = await price_of_test(test.test_code)
        button_text = f"{test.test_name} - {number_of_items} монет"
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, test=test.test_code, menu_type="1", i = number_of_items)

        markup.insert(InlineKeyboardMarkup(text=button_text, callback_data=callback_data))
    markup.row(
        InlineKeyboardButton(text="« Назад", callback_data=make_callback_data(level=CURRENT_LEVEL - 1, menu_type="1")))
    return markup

async def tests_keyboard_db():
    markup = InlineKeyboardMarkup(row_width=1)

    tests = await get_tests()
    for test in tests:
        button_text = f"{test.test_name}"
        exercises = await get_exercises_all(test.test_code)
        callback_data = make_callback_data_admin(level=13, test=test.test_code, i = 0, exercise=exercises[0].exercise_code)

        markup.insert(InlineKeyboardMarkup(text=button_text, callback_data=callback_data))
    markup.row(
        InlineKeyboardButton(text="« Закрыть", callback_data=make_callback_data_admin(level=-1)))
    return markup

async def confirm_entrance_keyboard(test, i):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup()
    exercises = await get_exercise(test=test)
    markup.row(InlineKeyboardButton(text="Да ✅",
                                    callback_data=make_callback_data(level=CURRENT_LEVEL + 2, menu_type="1", test=test, exercise=exercises[0].exercise_code,
                                                                     money=-i, item_id="1")),
               InlineKeyboardButton(text="Нет ❌",
                                    callback_data=make_callback_data(level=CURRENT_LEVEL - 1, menu_type="1")))
    return markup


async def confirm_exit_keyboard(test, exercise, i):
    CURRENT_LEVEL = 2
    markup = InlineKeyboardMarkup()

    markup.row(InlineKeyboardButton(text="Нет ❌", callback_data=make_callback_data(level=CURRENT_LEVEL + 2, menu_type="6",
                                                                                 test=test, exercise=exercise, i=i)),
               InlineKeyboardButton(text="Да ✅",
                                    callback_data=make_callback_data(level=CURRENT_LEVEL - 3, menu_type="10")))
    return markup


async def exercises_keyboard(test):
    CURRENT_LEVEL = 3
    markup = InlineKeyboardMarkup(row_width=1)
    exercises = await get_exercise(test)
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
        number_of_items = await count_screenshots(test_code=test, exercise_code=exercise.exercise_code)
        button_text = f"{exercise.exercise_name} ({number_of_items} скринш.)"
        callback_data = make_callback_data(level=CURRENT_LEVEL + 1, test=test, exercise=exercise.exercise_code,
                                           menu_type="1", i=0)

        markup.insert(InlineKeyboardMarkup(text=button_text, callback_data=callback_data))
    markup.row(InlineKeyboardButton(text="« Назад", callback_data=make_callback_data(level=CURRENT_LEVEL - 1, test=test,
                                                                                   menu_type="8")))
    return markup



async def screenshots_keyboard(test, exercise, i):
    CURRENT_LEVEL = 4
    markup = InlineKeyboardMarkup(row_width=1)
    screenshots = await get_screenshots(test, exercise)
    size = len(screenshots) - 1
    if int(i) + 1 > size:
        i1 = 0
    else:
        i1 = int(i) + 1
    if int(i) - 1 < 0:
        i2 = size
    else:
        i2 = int(i) - 1
    caption_screenshot = "скрин "+str(int(i) + 1) + "/" + str(size + 1)
    exercises = await get_exercise(test=test)
    exercise_index = -1
    for x in range(len(exercises)):
        if exercises[x].exercise_code==exercise:
            exercise_index = x
    exercise_index_prev = exercise_index - 1
    exercise_index_next = exercise_index + 1
    if exercise_index_prev + 1 == 0:
        exercise_index_prev = len(exercises) -1
    if exercise_index_next == len(exercises):
        exercise_index_next = 0

    exercise_index_str = str(exercise_index+1)
    caption_exercise = "задание " + exercise_index_str+ "/" + str(len(exercises))
    markup.row(InlineKeyboardButton(text="◀️", callback_data=make_callback_data(level=CURRENT_LEVEL, test=test,
                                                                                exercise=exercise, menu_type="6",
                                                                                i=i2)),
               InlineKeyboardButton(text=caption_screenshot, callback_data=make_callback_data(level=CURRENT_LEVEL, test=test,
                                                                                   exercise=exercise, menu_type="20",
                                                                                   i=i)),
               InlineKeyboardButton(text="▶️", callback_data=make_callback_data(level=CURRENT_LEVEL, test=test,
                                                                                exercise=exercise, menu_type="6",
                                                                                i=i1)))
    markup.row(InlineKeyboardButton(text="◀️", callback_data=make_callback_data(level=CURRENT_LEVEL, test=test,
                                                                                exercise=exercises[exercise_index_prev].exercise_code, menu_type="6",
                                                                                i=0)),
               InlineKeyboardButton(text=caption_exercise,
                                    callback_data=make_callback_data(level=CURRENT_LEVEL, test=test,
                                                                     exercise=exercise, menu_type="20",
                                                                     i=i)),
               InlineKeyboardButton(text="▶️", callback_data=make_callback_data(level=CURRENT_LEVEL, test=test,
                                                                                exercise=exercises[exercise_index_next].exercise_code, menu_type="6",
                                                                                i=0)))
    markup.row(InlineKeyboardButton(text="« Закрыть", callback_data=make_callback_data(level=CURRENT_LEVEL - 2, test=test, exercise=exercise, i=i,
                                                                                   menu_type="8")))
    return markup


async def screenshots_keyboard_db(test, exercise, i):
    markup = InlineKeyboardMarkup(row_width=1)
    screenshots = await get_screenshots_all(test, exercise)
    size = len(screenshots) - 1
    if int(i) + 1 > size:
        i1 = 0
    else:
        i1 = int(i) + 1
    if int(i) - 1 < 0:
        i2 = size
    else:
        i2 = int(i) - 1
    caption_screenshot = "скрин "+str(int(i) + 1) + "/" + str(size + 1)
    exercises = await get_exercises_all(test=test)
    exercise_index = -1
    for x in range(len(exercises)):
        if exercises[x].exercise_code==exercise:
            exercise_index = x
    exercise_index_prev = exercise_index - 1
    exercise_index_next = exercise_index + 1
    if exercise_index_prev + 1 == 0:
        exercise_index_prev = len(exercises) -1
    if exercise_index_next == len(exercises):
        exercise_index_next = 0

    tests = await get_tests()
    test_index = -1
    for x in range(len(tests)):
        if tests[x].test_code == test:
            test_index = x
    test_index_prev = test_index - 1
    test_index_next = test_index + 1
    if test_index_prev + 1 == 0:
        test_index_prev = len(tests) - 1
    if test_index_next == len(tests):
        test_index_next = 0
    exercises_prev = await get_exercises_all(test=tests[test_index_prev].test_code)
    exercises_next = await get_exercises_all(test=tests[test_index_next].test_code)
    exercise_index_str = str(exercise_index+1)
    test_index_str = str(test_index + 1)
    caption_exercise = "задание " + exercise_index_str+ "/" + str(len(exercises))
    caption_test = "тест " + test_index_str + "/" + str(len(tests))


    markup.row(InlineKeyboardButton(text="Открыть", callback_data=make_callback_data_admin(level=15, test=test,
                                                                                   exercise=exercise,
                                                                                   i=i)))
    markup.row(InlineKeyboardButton(text="◀️", callback_data=make_callback_data_admin(level=14, test=test,
                                                                                exercise=exercise,
                                                                                i=i2)),
               InlineKeyboardButton(text=caption_screenshot, callback_data=make_callback_data_admin(level=14, test=test,
                                                                                   exercise=exercise,
                                                                                   i=i)),
               InlineKeyboardButton(text="▶️", callback_data=make_callback_data_admin(level=14, test=test,
                                                                                exercise=exercise,
                                                                                i=i1)))
    markup.row(InlineKeyboardButton(text="◀️", callback_data=make_callback_data_admin(level=14, test=test,
                                                                                exercise=exercises[exercise_index_prev].exercise_code,
                                                                                i=0)),
               InlineKeyboardButton(text=caption_exercise,
                                    callback_data=make_callback_data_admin(level=14, test=test,
                                                                     exercise=exercise,
                                                                     i=i)),
               InlineKeyboardButton(text="▶️", callback_data=make_callback_data_admin(level=14, test=test,
                                                                                exercise=exercises[exercise_index_next].exercise_code,
                                                                                i=0)))
    markup.row(InlineKeyboardButton(text="◀️", callback_data=make_callback_data_admin(level=14, test=tests[test_index_prev].test_code,
                                                                                      exercise=exercises_prev[0].exercise_code,
                                                                                      i=0)),
               InlineKeyboardButton(text=caption_test,
                                    callback_data=make_callback_data_admin(level=14, test=test,
                                                                           exercise=exercise,
                                                                           i=i)),
               InlineKeyboardButton(text="▶️", callback_data=make_callback_data_admin(level=14, test=tests[test_index_next].test_code,
                                                                                      exercise=exercises_next[0].exercise_code,
                                                                                      i=0)))
    markup.row(InlineKeyboardButton(text="« Назад", callback_data=make_callback_data_admin(level=11)))
    return markup


async def unchaked_screenshots_keyboard(screenshots, i):
    markup = InlineKeyboardMarkup(row_width=1)
    size = len(screenshots) - 1
    if int(i) + 1 > size:
        i1 = 0
    else:
        i1 = int(i) + 1
    if int(i) - 1 < 0:
        i2 = size
    else:
        i2 = int(i) - 1
    caption = str(int(i) + 1) + " из " + str(size + 1)
    text = "Тема: {test} Номер задания: {exercise}".format(test=screenshots[int(i)].test_name,
                                                           exercise=screenshots[int(i)].exercise_name)
    markup.row(InlineKeyboardButton(text=text, callback_data=make_callback_data_admin(level=25)))
    markup.row(InlineKeyboardButton(text="◀️", callback_data=make_callback_data_admin(level=1, i=i2)),
               InlineKeyboardButton(text=caption, callback_data=make_callback_data_admin(level=1, i=i)),
               InlineKeyboardButton(text="▶️", callback_data=make_callback_data_admin(level=1, i=i1)))
    markup.row(InlineKeyboardButton(text="Принять ✅",
                                    callback_data=make_callback_data_admin(level=4, item_id=screenshots[int(i)].id, i=i)),
               InlineKeyboardButton(text="Отклонить ❌", callback_data=make_callback_data_admin(level=6, item_id=screenshots[int(i)].id, i=i)))
    markup.row(InlineKeyboardButton(text="Редактировать 📝", callback_data=make_callback_data_admin(level=2, item_id=screenshots[int(i)].id, i=i)))
    markup.row(InlineKeyboardButton(text="« Закрыть", callback_data=make_callback_data_admin(level=-1)))
    return markup


async def choose_money_to_add_keyboard(item_id, i):
    markup = InlineKeyboardMarkup(row_width=5)
    buttons = []
    buttons.append(InlineKeyboardButton(text='10', callback_data=make_callback_data_admin(level=5, item_id=item_id, money=10)))
    buttons.append(InlineKeyboardButton(text='15 (рек.)', callback_data=make_callback_data_admin(level=5, item_id=item_id, money=15)))
    buttons.append(InlineKeyboardButton(text='20', callback_data=make_callback_data_admin(level=5, item_id=item_id, money=20)))

    markup.add(*buttons)
    markup.row(InlineKeyboardButton(text="« Назад",
                                    callback_data=make_callback_data_admin(level=0, i=i)))
    return markup

async def choose_money_to_add_edit_keyboard(item_id, i):
    markup = InlineKeyboardMarkup(row_width=5)
    buttons = []
    for j in range(1, 16):
        buttons.append(InlineKeyboardButton(text=str(j),
                                    callback_data=make_callback_data_admin(level=5, item_id=item_id, money=j)))
    markup.add(*buttons)
    markup.row(InlineKeyboardButton(text="« Назад",
                                    callback_data=make_callback_data_admin(level=0, i=i)))
    return markup


async def edit_photo_from_predlozhka_keyboard(item_id, i):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text="тема",
                                    callback_data="change_test_{item_id}_{i}".format(item_id=item_id, i = i)))
    markup.row(InlineKeyboardButton(text="номер задания",
                                    callback_data="change_exercise_{item_id}_{i}".format(item_id=item_id, i = i)))
    markup.row(InlineKeyboardButton(text="фото",
                                    callback_data="change_photo_{item_id}_{i}".format(item_id=item_id, i = i)))
    return markup


async def choose_money_to_dismiss_keyboard(item_id, i):
    markup = InlineKeyboardMarkup()
    markup.row_width = 5
    buttons=[]
    buttons.append(InlineKeyboardButton(text=str(0), callback_data=make_callback_data_admin(level=7, item_id=item_id, money=0)))
    buttons.append(InlineKeyboardButton(text=str(5), callback_data=make_callback_data_admin(level=7, item_id=item_id, money=5)))
    markup.add(*buttons)
    markup.row(InlineKeyboardButton(text="« Назад",
                                    callback_data=make_callback_data_admin(level=0, i=i)))
    return markup


async def push_album_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Сменить номер задания",
                                    callback_data="push_album_exercise"))
    markup.row(InlineKeyboardButton(text="Сменить тему",
                                    callback_data="push_album_test"))
    markup.row(InlineKeyboardButton(text="« Выйти",
                                    callback_data="push_album_exit"))
    return markup


async def users_list_keyboard(i):
    markup = InlineKeyboardMarkup(row_width=1)
    users = await get_users()
    users.sort(key=lambda x: x.id)
    users_small = users[10*int(i):10*int(i)+10]
    for j in range (len(users_small)):
        button_text = f"{users_small[int(j)].full_name}"
        callback_data = make_callback_data_admin(level=12, item_id=users_small[int(j)].tg_id, i=i)

        markup.insert(InlineKeyboardMarkup(text=button_text, callback_data=callback_data))
    caption = f"{int(i)+1}/{(len(users)//10) + 1}"
    size = len(users) - 1
    if int(i) + 1 > (size//10):
        i1 = 0
    else:
        i1 = int(i) + 1
    if int(i) - 1 < 0:
        i2 = (size//10)
    else:
        i2 = int(i) - 1
    markup.row(InlineKeyboardButton(text="◀️", callback_data=make_callback_data_admin(level=10, i=i2)),
               InlineKeyboardButton(text=caption, callback_data=make_callback_data_admin(level=10, i=i)),
               InlineKeyboardButton(text="▶️", callback_data=make_callback_data_admin(level=10, i=i1)))
    markup.row(InlineKeyboardButton(text="« Закрыть", callback_data=make_callback_data_admin(level=-1)))
    return markup

async def users_info_keyboard(i, item_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="« Назад", callback_data=make_callback_data_admin(level=10, i=i)))
    return markup

async def users_info_keyboard_from_screenshot(i, test, exercise):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="« Назад", callback_data=make_callback_data_admin(level=15, i=i, test=test,
                                                                                           exercise=exercise)))
    return markup

async def screen_info_db_keyboard(i, test, exercise, item_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text="Редактировать", callback_data=make_callback_data_admin(level=17, i=i, test=test,
                                                                                           exercise=exercise)))

    markup.row(
        InlineKeyboardButton(text="Инфо по автору", callback_data=make_callback_data_admin(level=16, i=i, item_id=item_id, test=test, exercise=exercise)))
    markup.row(InlineKeyboardButton(text="« Назад", callback_data=make_callback_data_admin(level=13, i=i, test=test, exercise=exercise)))
    return markup


async def edit_photo_from_db_keyboard(test, exercise, i):
    markup = InlineKeyboardMarkup()
    photos = await get_screenshots_all(test_code=test, exercise_code=exercise)
    item = await get_screenshot(screenshot_id=photos[int(i)].id)
    markup.row(InlineKeyboardButton(text="Тема",
                                    callback_data="test_{item_id}_{i}".format(item_id=item.id, i = i)))
    markup.row(InlineKeyboardButton(text="Номер задания",
                                    callback_data="exercise_{item_id}_{i}".format(item_id=item.id, i = i)))
    markup.row(InlineKeyboardButton(text="Фото",
                                    callback_data="photo_{item_id}_{i}".format(item_id=item.id, i = i)))
    if item.isDeleted:
        markup.row(InlineKeyboardButton(text="Восстановить",
                                    callback_data="delete_{item_id}_{i}".format(item_id=item.id, i=i)))
    else:
        markup.row(InlineKeyboardButton(text="Удалить",
                                        callback_data="delete_{item_id}_{i}".format(item_id=item.id, i=i)))
    markup.row(InlineKeyboardButton(text="Отмена",
                                        callback_data="return_{item_id}_{i}".format(item_id=item.id, i=i)))
    return markup