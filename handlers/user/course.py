from aiogram import Router, Dispatcher, types, F
from loader import db, dp, bot
from data import CourseButtonType
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import sleep
from states.user import UserStates
from utils import TestManager


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
                manager = TestManager(tests, mix_tests=button.mix_tests, time=button.time)
                test = manager.pop_test()
                if test.question_long:
                    text=f", {manager.time_left}]" if manager.time else ']'
                    await update.answer(f"[{test.number}/{len(tests)}"+text, )

                if test.media:
                    await bot.copy_message(chat_id=update.from_user.id, 
                                        message_id=test.media,
                                        protect_content=db.PROTECT_CONTENT,
                                        from_chat_id=db.DATA_CHANEL_ID)

                m = await update.answer_poll(question = test.display_question(manager.time_left),
                                         options = test.mixsed_options,
                                         correct_option_id = test.correct_index,
                                         type='quiz',
                                         protect_content=db.PROTECT_CONTENT,
                                         explanation=test.info,
                                         is_anonymous=False,
                                         reply_markup=KeyboardManger.test_buttons(manager.tests_leng))
                await state.set_state(UserStates.in_test)
                await state.update_data(manager = manager, poll_id = m.poll.id, course_button_id = button.id)
            else:
                # await update.answer_sticker('CAACAgIAAxkBAAIHbGiPFIlhq8G6gLcKvA-jWf1yz2kIAAL5AANWnb0KlWVuqyorGzY2BA')
                await update.answer(f"{button.name} da hozirda birortaham test yo'q", reply_markup=KeyboardManger.course_menu(buttons, pro = course.pro)) 
            
    else:
        if course.pro:
            await update.answer(f"{course.name} kursi", reply_markup=KeyboardManger.course_menu(buttons, pro = course.pro, subscribed = bool(sub)))
        else:
            await update.answer(f"{course.name} kursi", reply_markup=KeyboardManger.course_menu(buttons, pro = course.pro)) 

