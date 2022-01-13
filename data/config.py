import os

from dotenv import load_dotenv
from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))


PGUSER = str(os.getenv("PGUSER"))
PGPASSWORD = str(os.getenv("PGPASSWORD"))
DATABASE = str(os.getenv("DATABASE"))
ip = os.getenv("ip")
ADMIN_CHAT_ID = str(os.getenv("ADMIN_CHAT_ID"))
POSTGRESURI = f"postgresql://{PGUSER}:{PGPASSWORD}@{ip}/{DATABASE}"
aiogram_redis = {'host': ip,}

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
admins = env.list("ADMINS")  # Тут у нас будет список из админов
IP = env.str("ip")  # Тоже str, но для айпи адреса хоста

