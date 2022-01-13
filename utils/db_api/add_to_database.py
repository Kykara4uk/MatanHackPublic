import asyncio

from utils.db_api.database import create_db
from utils.db_api.db_commands import add_item


async def add_items():
    await add_item(test_name="ФКЗ22", test_code="11", exercise_name="1", exercise_code="1", photo="-", isCheck= True)
    await add_item(test_name="ФКЗ1", test_code="12", exercise_name="2", exercise_code="2", photo="-", isCheck= True)
    await add_item(test_name="ФКЗ2", test_code="13", exercise_name="3", exercise_code="3", photo="-", isCheck= True)
    await add_item(test_name="ФКЗ3", test_code="14", exercise_name="4", exercise_code="4", photo="-", isCheck= True)
    await add_item(test_name="ФКЗ4", test_code="15", exercise_name="5", exercise_code="5", photo="-", isCheck= True)
    await add_item(test_name="Комплексні числа1", test_code="21", exercise_name="1", exercise_code="1", photo="-", isCheck= True)
    await add_item(test_name="Комплексні числа2", test_code="22", exercise_name="2", exercise_code="2", photo="-", isCheck= True)
    await add_item(test_name="Комплексні числа3", test_code="23", exercise_name="3", exercise_code="3", photo="-", isCheck= True)
    await add_item(test_name="Комплексні числа4", test_code="24", exercise_name="4", exercise_code="4", photo="-", isCheck= True)
    await add_item(test_name="Комплексні числа5", test_code="25", exercise_name="5", exercise_code="5", photo="-", isCheck= True)
loop = asyncio.get_event_loop()
loop.run_until_complete(create_db())
loop.run_until_complete(add_items())