from aiogram import Router, Dispatcher, types, F
from loader import db, dp, bot
from data import CourseButtonType
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import sleep
from states.user import UserStates



r = Router()
dp.include_router(r)

@r.message(UserStates.course_menu)
async def course_menu_handler(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.clear()
        subs = [sub.course for sub in await db.get_subscribtions(update.from_user.id)]
        await update.answer("🏠 Bosh menyu", reply_markup=KeyboardManger.home(await db.get_courses(), subs = subs))
        return
    
    data = await state.get_data()
    course = await db.get_course(id = data['course_id'])
    buttons = await db.get_course_buttons(course.id)
    button = await db.get_course_button(course_id=course.id, name=update.text[2:] if update.text.startswith('🔒 ') else update.text)
    sub = await db.get_subscribtion(user_id=update.from_user.id, course=course.id)
    if button:
        if course.pro and not button.open and not sub:
            if course.message:
                await bot.copy_message(chat_id=update.from_user.id,
                                        message_id=course.message,
                                        from_chat_id=db.DATA_CHANEL_ID,
                                        reply_markup=InlineKeyboardManager.buy_course(db.CONTACT_ADMIN))
            else:
                await update.answer("👑 Ushbu kursdan foydlanish uchun kursni sotib olishingiz kerak. Sotib olish uchun adminga yozing",
                                    reply_markup=InlineKeyboardManager.buy_course(db.CONTACT_ADMIN))

        elif button.type == CourseButtonType.MEDIA:
            if button.media:
                await bot.copy_messages(chat_id=update.from_user.id, 
                                    message_ids=button.media,
                                    protect_content=db.PROTECT_CONTENT,
                                    from_chat_id=db.DATA_CHANEL_ID)
            else:
                await update.answer("⚡️ Tez orada yuklandadi")

        elif button.type == CourseButtonType.TEST:
            tests = await db.get_tests(button.id)
            if tests:
                pass
            else:
                await update.answer_sticker('CAACAgIAAxkBAAIHbGiPFIlhq8G6gLcKvA-jWf1yz2kIAAL5AANWnb0KlWVuqyorGzY2BA')
                await update.answer(f"{button.name} da hozirda birortaham test yo'q", reply_markup=KeyboardManger.course_menu(buttons, pro = course.pro)) 
            
    else:
        if course.pro:
            await update.answer(f"{course.name} kursi", reply_markup=KeyboardManger.course_menu(buttons, pro = course.pro, subscribed = bool(sub)))
        else:
            await update.answer(f"{course.name} kursi", reply_markup=KeyboardManger.course_menu(buttons, pro = course.pro)) 




async def send_mdia(update: types.Message, state: FSMContext):
    pass