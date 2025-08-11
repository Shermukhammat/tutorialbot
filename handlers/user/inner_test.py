from aiogram import Router, Dispatcher, types, F
from loader import db, dp, bot
from data import CourseButtonType
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import sleep, Semaphore
from states.user import UserStates, InnerMenu
from utils import TestManager



r = Router()
dp.include_router(r)
sema = Semaphore()



async def test_finished(user_id: int, state: FSMContext):
    await state.set_state(InnerMenu.main)

    data = await state.get_data()
    course = await db.get_course(id = data['course_id'])
    manager : TestManager = data['manager']
    button = await db.get_course_button(id = data['course_button_id'])
    inner_button = await db.get_course_inner_button(id = data['inner_button_id'])
    inner_buttons = await db.get_course_inner_buttons(button.id)
    sub = await db.get_subscribtion(user_id=user_id, course=course.id)
    reply_markup=KeyboardManger.inner_menu(inner_buttons, pro = course.pro, subscribed = bool(sub))
    
    if not manager.time_is_up:
        if manager.correct_prestage > 90:
            await bot.send_message(text='🎉', chat_id=user_id)
        else:
            await bot.send_message(text='🏁', chat_id=user_id)

        if inner_button.media:
            await bot.copy_messages(chat_id=user_id,
                                    message_ids=inner_button.media,
                                    from_chat_id=db.DATA_CHANEL_ID)
        text = f"🏁 {inner_button.name} testi tugadi \n🔢 Jami test: {manager.tests_leng_static} \n✅ To'g'ri: {manager.correct} \n❌ Xato: {manager.incorrect} \n📝 Ball to'pladingiz: {manager.correct_prestage}"
    else:
        await bot.send_message(text='⏳', chat_id=user_id)
        text = f"🏁 {inner_button.name} testo uchun ajratilgan vaxt tugadi \n🔢 Jami test: {manager.tests_leng_static} \n✅ To'g'ri: {manager.correct} \n❌ Xato: {manager.incorrect} \n📝 Ball to'pladingiz: {manager.correct_prestage}"

    await bot.send_message(text = text,
                           chat_id = user_id,  
                           reply_markup = reply_markup)



@dp.poll_answer(InnerMenu.in_test)
async def poll_answer_handler(answer: types.PollAnswer, state: FSMContext):
    data = await state.get_data()
    poll_id = data['poll_id']
    manager: TestManager = data['manager']
    if answer.poll_id  != poll_id:
        return
    
    if manager.time_is_up:
        await test_finished(answer.user.id, state)
        return
    
    chosen = answer.option_ids[0] if answer.option_ids else None
    manager.check_test(chosen)
    
    

    test = manager.pop_test()
    if not test:
        await test_finished(answer.user.id, state)
        return
 
    if test.media:
        await bot.copy_message(chat_id=answer.user.id, 
                               message_id = test.media,
                               protect_content=db.PROTECT_CONTENT,
                               from_chat_id=db.DATA_CHANEL_ID)
  
    if test.question_long:
        text = f", {manager.time_left}]" if manager.time else ']'
        await bot.send_message(text = f"[{test.number}/{test.tests_leng}" + text, chat_id=answer.user.id)
    
    m = await bot.send_poll(question = test.display_question(manager.time_left),
                                chat_id = answer.user.id,
                                options = test.mixsed_options,
                                correct_option_id = test.correct_index,
                                type='quiz',
                                is_anonymous=False,
                                protect_content=db.PROTECT_CONTENT,
                                explanation=test.info,
                                reply_markup=KeyboardManger.test_buttons(manager.tests_leng))
    await state.update_data(manager = manager, message_id = m.message_id, poll_id = m.poll.id)



@dp.message(InnerMenu.in_test, F.text == '➡️ Keyingi')
async def skip_test(update: types.Message, state: FSMContext):
    async with sema:
        data = await state.get_data()
        manager: TestManager = data['manager']
        message_id = data.get('message_id')


        if manager.time_is_up:
            await test_finished(update.from_user.id, state)
            return
        
        test = manager.skip_test()
        if test:
            try:
                await bot.delete_message(chat_id=update.from_user.id, message_id=message_id)
            except:
                pass
            
            if test.question_long:
                text=f", {manager.time_left} min]" if manager.time else ']'
                await update.answer(f"[{test.number}/{test.tests_leng}"+text, )

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
            await state.update_data(manager = manager, message_id = m.message_id, poll_id = m.poll.id)

        else:
            await update.answer("❗️ Boshqa test yo'q", reply_markup=KeyboardManger.test_buttons(manager.tests_leng))


@dp.message(InnerMenu.in_test)
async def test_handler(update: types.Message, state: FSMContext):
    if update.text == "❌ Bekor qilish":
        await state.set_state(InnerMenu.main)
        data = await state.get_data()
        course = await db.get_course(id = data['course_id'])
        button = await db.get_course_button(id = data['course_button_id'])
        inner_buttons = await db.get_course_inner_buttons(button.id)
        inner_button = await db.get_course_inner_button(id = data['inner_button_id'])
        sub = await db.get_subscribtion(user_id=update.from_user.id, course=course.id)
        
        await update.answer(f"{inner_button.name} menyusi", reply_markup=KeyboardManger.inner_menu(inner_buttons, pro = course.pro, subscribed = bool(sub)))


    else:
        data = await state.get_data()
        manager: TestManager = data['manager']
        if manager.time_is_up:
            return await test_finished(update.from_user.id, state)

        await update.answer("Iltimos yuqoridagi tesga javob bering", reply_markup=KeyboardManger.test_buttons(manager.tests_leng))
    
