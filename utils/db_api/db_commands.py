from typing import List

from sqlalchemy import and_

from utils.db_api.database import db
from utils.db_api.models import Screenshots
from utils.db_api.models import Users

async def add_item(**kwargs):
    newitem = await Screenshots(**kwargs).create()
    return newitem
async def get_tests() -> List[Screenshots]:
    return await Screenshots.query.distinct(Screenshots.test_code).gino.all()


async def get_checked_tests() -> List[Screenshots]:
    return await Screenshots.query.where(Screenshots.isCheck == True).distinct(Screenshots.test_code).gino.all()

async def vidminok(coins): # я не знал куда впихнуть эту функцию, поэтому пусть пока тут будет
    coins = int(coins)
    tcoins=coins
    if coins<0:
        coins*=-1
    k=coins%10
    if coins>=10 and coins<=20:
        word='монеток'
    elif k == 1:
            word='монета'
    elif k>=2 and k<=4:
        word='монеты'
    else:
        word='монеток'
    return str(tcoins)+' '+word

async def get_test_name(test_code):
    test = await Screenshots.query.where(Screenshots.test_code == test_code).gino.first()
    test_name = test.test_name
    return test_name

async def get_test_code(test_name):
    test = await Screenshots.query.where(Screenshots.test_name == test_name).gino.first()
    try:
        test_code = test.test_code
    except AttributeError:
        tests = await get_tests()
        max_code = 0
        for test2 in tests:
            if int(test2.test_code) > max_code:
                max_code = int(test2.test_code)
        test_code = str(max_code + 1)
    return test_code

async def get_exercise_name(exercise_code):
    exercise = await Screenshots.query.where(Screenshots.exercise_code == exercise_code).gino.first()
    exercise_name = exercise.test_name
    return exercise_name

async def get_exercise_code(exercise_name, test_code):
    exercise = await Screenshots.query.where(and_(Screenshots.test_code==test_code, Screenshots.exercise_name == exercise_name)).gino.first()
    try:
        exercise_code = exercise.exercise_code
    except AttributeError:
        exercises = await get_exercises()
        max_code = 0
        for exercise2 in exercises:
            if int(exercise2.exercise_code) > max_code:
                max_code = int(exercise2.exercise_code)
        exercise_code = str(max_code + 1)
    return exercise_code

async def get_exercise(test) -> List[Screenshots]:
    return await Screenshots.query.distinct(Screenshots.exercise_code).where(and_(Screenshots.test_code == test, Screenshots.isCheck==True, Screenshots.isDeleted==False)).gino.all()

async def get_exercises_all(test) -> List[Screenshots]:
    return await Screenshots.query.distinct(Screenshots.exercise_code).where(and_(Screenshots.test_code == test)).gino.all()


async def get_exercises() -> List[Screenshots]:
    return await Screenshots.query.distinct(Screenshots.exercise_code).gino.all()

async def count_screenshots(test_code, exercise_code = None):
    conditions = [Screenshots.test_code == test_code, Screenshots.isCheck == True, Screenshots.isDeleted == False]
    if exercise_code:
        conditions.append((Screenshots.exercise_code == exercise_code))
    total = await db.select([db.func.count()]).where(
        and_(*conditions)
    ).gino.scalar()
    return total


async def price_of_test(test_code):


    total = await Screenshots.query.distinct(Screenshots.exercise_code).where(and_(Screenshots.test_code == test_code, Screenshots.isCheck==True, Screenshots.isDeleted==False)).gino.all()
    price = len(total) * 10
    return price


async def get_screenshots(test_code, exercise_code) -> List[Screenshots]:
    screenshots = await Screenshots.query.where(
        and_(Screenshots.test_code == test_code, Screenshots.exercise_code == exercise_code, Screenshots.isCheck == True, Screenshots.isDeleted == False)
    ).gino.all()
    return screenshots

async def get_screenshots_all(test_code, exercise_code) -> List[Screenshots]:
    screenshots = await Screenshots.query.where(
        and_(Screenshots.test_code == test_code, Screenshots.exercise_code == exercise_code)
    ).gino.all()
    return screenshots


async def get_unchaked_screenshots() -> List[Screenshots]:
    screenshots = await Screenshots.query.where(
        Screenshots.isCheck == False
    ).gino.all()
    return screenshots


async def get_screenshot(screenshot_id) -> Screenshots:
    screenshot = await Screenshots.query.where(Screenshots.id == screenshot_id).gino.first()
    return screenshot


async def get_user(user_id) -> Users:
    user = await Users.query.where(Users.tg_id == user_id).gino.first()
    return user


async def get_users() -> List[Users]:
    users = await Users.query.gino.all()
    return users


async def add_user(**kwargs):
    newuser = await Users(**kwargs).create()
    return newuser

async def get_referrals(user_id):
    referral = await Users.query.where(Users.referal == user_id).gino.all()
    return referral

async def get_referral_link(user_id):
    user = await Users.query.where(Users.tg_id == user_id).gino.first()
    referral_link =user.referal_code
    return referral_link

async def change_money(money, user_id):
    user = await get_user(user_id)
    balance = int(user.balance)+int(money)
    await user.update(balance=str(balance)).apply()


async def activate_referal(user_id):
    user = await get_user(user_id)
    await user.update(isReferalActivated=True).apply()

async def get_referral_status(user_id):
    user = await Users.query.where(Users.tg_id == user_id).gino.first()
    referral_status =user.isReferalActivated
    return referral_status


async def check_money(user_id):
    user = await get_user(user_id)
    balance = user.balance
    return balance