from aiogram import Router, Dispatcher, types, F
from loader import db, dp
from buttons import KeyboardManger
from aiogram.fsm.context import FSMContext
from asyncio import sleep
r = Router()
dp.include_router(r)



@r.message(F.content_type.in_({types.ContentType.STICKER,}))
async def get_sticer_file_id(update : types.Message, state: FSMContext):
    await update.answer(f"`{update.sticker.file_id}`", parse_mode="MarkdownV2")

@r.message()
async def main_handler(update : types.Message):
    subs = [sub.course for sub in await db.get_subscribtions(update.from_user.id)]
    await update.answer("🏠 Bosh menyu", reply_markup=KeyboardManger.home(await db.get_courses(), subs = subs))
