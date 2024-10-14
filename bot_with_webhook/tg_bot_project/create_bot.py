# Aiogram import`s
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Data import`s
from dotenv import load_dotenv
import os

# Main var`s

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
WEBHOOK_PATH = f'/{BOT_TOKEN}'
BASE_URL = os.getenv('URL')
ADMIN_ID = os.getenv('ADMIN_ID')
DIR_DOWNLOAD = os.getenv('DIR_DOWNLOAD')

# Init bot and dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

