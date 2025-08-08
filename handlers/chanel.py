from loader import dp, db, bot
from aiogram import types, F
from data import User, UserStatus
from aiogram.filters import Command, CommandStart, CommandObject
from buttons import KeyboardManger
from aiogram.fsm.context import FSMContext
from states import AdminPanel
from asyncio import Semaphore, sleep
from states.user import UserStates



@dp.channel_post()
async def give_id(update: types.Message):
    if update.text and update.text.startswith('/id'):
        p = await update.reply(f"id: `{update.chat.id}`", parse_mode='markdown')
        await sleep(3)
        await p.delete()
        await update.delete()
        


@dp.callback_query(F.data == 'check')
async def update(callback: types.CallbackQuery):
    await callback.answer("✅ Botdan foydalanishingiz mumkin", show_alert=True)
    await sleep(1)
    await callback.message.delete()