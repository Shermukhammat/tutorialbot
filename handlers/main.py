from aiogram import Router, Dispatcher, types, F
from loader import db, dp
from buttons import KeyboardManger
from aiogram.fsm.context import FSMContext

mr = Router()
dp.include_router(mr)

@mr.message()
async def main_handler(update : types.Message):
    await update.answer("❗️ Nomalum buyruq", reply_markup=KeyboardManger.home(await db.get_courses()))



@mr.message(F.content_type.in_({types.ContentType.STICKER}))
async def get_sticer_file_id(update : types.Message, state: FSMContext):
    await update.answer(f"`{update.sticker.file_id}`", parse_mode="MarkdownV2")