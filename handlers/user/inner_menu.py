from aiogram import Router, Dispatcher, types, F
from loader import db, dp, bot
from data import CourseButtonType
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import sleep
from states.user import UserStates, InnerMenu
from utils import TestManager


r = Router()
dp.include_router(r)

@r.message(InnerMenu.main)
async def course_inner_menu_handler(update: types.Message, state: FSMContext):
    data = await state.get_data()
    course = await db.get_course(id = data['course_id'])
    button = await db.get_course_button(id = data['course_button_id'])
    sub = await db.get_subscribtion(user_id=update.from_user.id, course=course.id)

    if update.text == "⬅️ Orqaga":
        buttons = await db.get_course_buttons(course.id)
        await state.set_state(UserStates.course_menu)
        await update.answer(f"{course.name} kursi", reply_markup=KeyboardManger.course_menu(buttons, pro = course.pro, subscribed = bool(sub)))
        return
    
    inner_button = await db.get_course_inner_button(course_button=button.id, name=update.text[2:] if update.text.startswith('🔒 ') else update.text)
    if inner_button:
        if course.pro and not inner_button.open and not sub:
            if course.message:
                await bot.copy_message(chat_id=update.from_user.id,
                                        message_id=course.message,
                                        from_chat_id=db.DATA_CHANEL_ID,
                                        reply_markup=InlineKeyboardManager.buy_course(db.CONTACT_ADMIN))
            else:
                await update.answer("👑 Ushbu kursdan foydlanish uchun kursni sotib olishingiz kerak. Sotib olish uchun adminga yozing",
                                    reply_markup=InlineKeyboardManager.buy_course(db.CONTACT_ADMIN))

        elif inner_button.type == CourseButtonType.MEDIA:
            if inner_button.media:
                await bot.copy_messages(chat_id=update.from_user.id, 
                                    message_ids=inner_button.media,
                                    protect_content=db.PROTECT_CONTENT,
                                    from_chat_id=db.DATA_CHANEL_ID)
            else:
                await update.answer("⚡️ Tez orada yuklandadi")

        elif inner_button.type == CourseButtonType.TEST:
            tests = await db.get_tests(inner_button = inner_button.id)
            if tests:
                manager = TestManager(tests, mix_tests=inner_button.mix_tests, time=inner_button.time)
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
                await state.set_state(InnerMenu.in_test)
                await state.update_data(manager = manager, poll_id = m.poll.id, message_id = m.message_id, course_button_id = button.id, inner_button_id = inner_button.id)
            else:
                # await update.answer_sticker('CAACAgIAAxkBAAIHbGiPFIlhq8G6gLcKvA-jWf1yz2kIAAL5AANWnb0KlWVuqyorGzY2BA')
                inner_buttons = await db.get_course_inner_buttons(button.id)
                await update.answer(f"{inner_button.name} da hozirda birortaham test yo'q", reply_markup=KeyboardManger.course_menu(inner_buttons, pro = course.pro, subscribed = bool(sub))) 
        
    else:
        inner_buttons = await db.get_course_inner_buttons(button.id)
        await update.answer(f"{button.name} menyusi", reply_markup=KeyboardManger.inner_menu(inner_buttons, pro = course.pro, subscribed = bool(sub)))

