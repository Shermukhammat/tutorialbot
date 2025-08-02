from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from data import DataBase

db = DataBase('files/config.yaml')
bot = Bot(db.TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp['bot'] = bot