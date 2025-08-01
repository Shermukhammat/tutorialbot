from aiogram import Bot, Dispatcher
from data import DataBase

db = DataBase('files/config.yaml')
bot = Bot(db.TOKEN)
dp = Dispatcher()
dp['bot'] = bot