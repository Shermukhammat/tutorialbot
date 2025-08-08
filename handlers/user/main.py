from aiogram import Router, Dispatcher, types, F
from loader import db, dp, bot
from buttons import KeyboardManger
from aiogram.fsm.context import FSMContext
from asyncio import sleep
from states.user import UserStates



r = Router()
dp.include_router(r)



@dp.message(F.text == '📖 Yordam')
async def help_button(update: types.Message):
    if db.HELP_CONTENT:
        await bot.copy_message(chat_id=update.from_user.id,
                               from_chat_id=db.DATA_CHANEL_ID,
                               message_id=db.HELP_CONTENT)
    else:
        await update.answer("⚡️ Yordam ma'lumoti tez orada yuklanadi")

@r.message(F.content_type.in_({types.ContentType.STICKER,}))
async def get_sticer_file_id(update : types.Message, state: FSMContext):
    await update.answer(f"`{update.sticker.file_id}`", parse_mode="MarkdownV2")

@r.message(F.content_type.in_({types.ContentType.TEXT}))
async def main_handler(update : types.Message, state: FSMContext):
    user = await db.get_user(update.from_user.id)
    course = await db.get_course(name=update.text[2:] if update.text.startswith('👑 ') else update.text)
    if course:
        await state.set_state(UserStates.course_menu)
        await state.update_data(course_id = course.id)
        buttons = await db.get_course_buttons(course.id)

        if course.pro:
            sub = await db.get_subscribtion(course=course.id, user_id=update.from_user.id)
            if sub and not user.phone_number:
                await state.set_state(UserStates.get_phone_number)
                await state.update_data(course_id = course.id)
                await update.answer("Kursdan foydlanish uchun telfon raqamni yuborish tugmasni bosing",
                                    reply_markup = KeyboardManger.request_phone_number())
                return
            
            await update.answer(f"{course.name} kursi", reply_markup=KeyboardManger.course_menu(buttons, pro = course.pro, subscribed = bool(sub)))
        else:
            await update.answer(f"{course.name} kursi", reply_markup=KeyboardManger.course_menu(buttons, pro = course.pro)) 
    else:
        subs = [sub.course for sub in await db.get_subscribtions(update.from_user.id)]
        await update.answer("🏠 Bosh menyu", reply_markup=KeyboardManger.home(await db.get_courses(), subs = subs))

