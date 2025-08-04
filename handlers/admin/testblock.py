from aiogram import Router, Dispatcher, types, F
from states import AdminPanel, AdminCourseMneu, AdminCourseButton, AdminTestBlock
from loader import db, dp
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import Semaphore
from data import Course, CourseButtonType, Test 
from utils.mytime import can_edit
from .main import r, sema, back_to_course_menu
from aiogram.types import ContentType
from asyncio import sleep


@r.message(AdminTestBlock.main)
async def edit_test_block(update : types.Message, state: FSMContext):
    data = await state.get_data()
    course_id = data.get('course_id')
    button_id = data.get('button_id')
    course = await db.get_course(id = course_id)
    button = await db.get_course_button(id = button_id)
    
    if update.text == "⬅️ Orqaga":
        await back_to_course_menu(update, state)
        
    elif update.text == "➕ Test qo'shish":
        await state.set_state(AdminTestBlock.get_test)
        await state.update_data(media = None)
        tests = await db.get_tests(course_button_id=button_id)
        await update.answer(f"🧪 Menga {len(tests)+1}-savolingiz bilan soʻrovnoma yuboring. Bunga muqobil ravishda, bu savoldan oldin koʻrsatiladigan matn yoki mediafayl bilan xabar yuborishingiz mumkin.", 
                            reply_markup=KeyboardManger.make_quiz())

    elif update.text == "📋 Testlar":
        tests = await db.get_tests(course_button_id=button_id)
        tests_len = len(tests)
        if tests:
            text = f"1/{tests_len if tests_len < 10 else 10}  dan {tests_len} Testlar:"
            for index, test in enumerate(tests[:10]):
                text += f"\n{index+1}. {test.question}"

            await update.answer(text, reply_markup=InlineKeyboardManager.tests_paginator(tests, per_page = 10))
        else:
            await update.answer_sticker("CAACAgIAAxkBAAIHbGiPFIlhq8G6gLcKvA-jWf1yz2kIAAL5AANWnb0KlWVuqyorGzY2BA")
            await sleep(1)
            await update.answer("Birotaham test yo'q", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))
    
    elif update.text == "✅ Qator tashla":
        await db.update_course_button(id = button.id, new_line = False)
        button.new_line = False
        await update.answer("✅ Endi tugmadan oldin yangi qator tashlanmaydi", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))

    elif update.text == "❌ Qator tashla":
        await db.update_course_button(id = button.id, new_line = True)
        button.new_line = True
        await update.answer("✅ Endi tugmadan oldin yangi qator tashlanadi", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))

    elif update.text == "✏️ Nomi":
        await state.set_state(AdminTestBlock.edit_name)
        await update.answer(f"{button.name} test blogni yangi nomini kirting ✍️", reply_markup=KeyboardManger.back())

    elif update.text.startswith("⏳ Vaxt"):
        await state.set_state(AdminTestBlock.edit_time)
        await update.answer(f"{button.name} test blogi uchun test vaxtni kirting mintuda", reply_markup=KeyboardManger.time_button())

    elif update.text == "✅ Testlarni arlashtir":
        await db.update_course_button(id = button.id, mix_tests = False)
        button.mix_tests = False
        await update.answer("✅ Testlar arlshtirish o'chirldi", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))
    
    elif update.text == "❌ Testlarni arlashtir":
        await db.update_course_button(id = button.id, mix_tests = True)
        button.mix_tests = True
        await update.answer("✅ Testlar arlshtirish yoqildi", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))    

    elif update.text == "✅ Varyantlarni arlashtir":
        await db.update_course_button(id = button.id, mix_options = False)
        button.mix_options = False
        await update.answer("✅ Varyantlar arlshtirish o'chirldi", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))

    elif update.text == "❌ Varyantlarni arlashtir":
        await db.update_course_button(id = button.id, mix_options = True)
        button.mix_options = True
        await update.answer("✅ Varyantlar arlshtirish yoqildi", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))

    elif update.text == "🔒 Yopiq":
        await db.update_course_button(id = button.id, open = True)
        button.open = True
        await update.answer("✅ Endi test blogni obuna bo'lmasdan foydalanish mumkin", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))

    elif update.text == "🔓 Ochiq":
        await db.update_course_button(id = button.id, open = False)
        button.open = False
        await update.answer("✅ Endi test blogni obuna bo'lmasdan foydalanish mumkin emas", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))

    elif update.text == "🗑 O'chirish":
        await state.set_state(AdminTestBlock.delete)
        await update.answer("☠️")
        await update.answer(f"{button.name} test blogni xaqiqatdan ham o'chirmoqchimisi?", reply_markup=KeyboardManger.yes_or_no())

    else:
        await update.answer(f"Test blog: {button.name}", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))


@r.message(AdminTestBlock.delete)
async def delete_block(update: types.Message, state: FSMContext):
    data = await state.get_data()
    course = await db.get_course(id = data['course_id'])
    button = await db.get_course_button(id = data['button_id'])

    if update.text == "✅ Xa":
        data = await state.get_data()
        await db.delete_course_button(button.id)
        await back_to_course_menu(update, state)
    else:
        await state.set_state(AdminTestBlock.main)
        await update.answer("O'chrish bekor qilindi", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))

@r.message(AdminTestBlock.edit_time)
async def edit_time(update: types.Message, state: FSMContext):
    data = await state.get_data()
    course = await db.get_course(id = data['course_id'])
    button = await db.get_course_button(id = data['button_id'])

    if update.text == "⬅️ Orqaga":
        await state.set_state(AdminTestBlock.main)
        await update.answer(f"Test blgo: {button.name}", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))
    
    elif update.text == "♾️ Vaxt belgilanmasin":
        await db.update_course_button(button.id, time = None)
        button.time = None
        await state.set_state(AdminTestBlock.main)
        await update.answer(f"✅ Vaxt endi cheklanmagan", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))

    elif update.text.isnumeric():
        await db.update_course_button(button.id, time = int(update.text))
        await state.set_state(AdminTestBlock.main)
        button.time = int(update.text)
        await update.answer(f"✅ Vaxt yangilandi", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))

    else:
        await update.reply("❗️ Iltimos faqat raqam ko'nishda vaxtni kirting", reply_markup=KeyboardManger.time_button())

@r.message(AdminTestBlock.edit_name)
async def edit_name(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        data = await state.get_data()
        course = await db.get_course(id = data['course_id'])
        button = await db.get_course_button(id = data['button_id'])
        await state.set_state(AdminTestBlock.main)
        await update.answer(f"Test blgo: {button.name}", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))
    else:
        async with sema:
            data = await state.get_data()
            button_id = data.get('button_id')
            course = await db.get_course(id = data['course_id'])
            button = await db.get_course_button(id = button_id)
            buttons = await db.get_course_buttons(course_id=data['course_id'])

            if update.text in [button.name for button in buttons]:
                await update.reply("❗️ Bunday nomli tugma mavjud", reply_markup=KeyboardManger.back())
            
            elif len(update.text) > 35:
                await update.reply("❗️ Tugma nomi 35 ta belgidan ko'p bo'lmasligi kerak", reply_markup=KeyboardManger.back())
            else:
                await db.update_course_button(button.id, name = update.text)
                await state.set_state(AdminTestBlock.main)
                await update.answer("✅ Test blog nomi o'zgartirildi", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))
                
@r.callback_query(AdminTestBlock.main, F.data.startswith('edit_'))
async def edit_test(update: types.CallbackQuery, state: FSMContext):
    test_id = int(update.data.replace('edit_', ''))
    test = await db.get_test(test_id)   
    data = await state.get_data()
    button_id = data.get('button_id')
    tests = await db.get_tests(course_button_id=button_id)

    index = [test.id for test in tests].index(test.id)

    await state.set_state(AdminTestBlock.edit_test)
    await state.update_data(media = None, test_id = test_id)
    await update.message.answer(f"{index+1}-testni qaytadan kirting", reply_markup=KeyboardManger.make_quiz())

@r.message(AdminTestBlock.edit_test, F.content_type.in_(
        {ContentType.PHOTO, ContentType.VOICE, ContentType.AUDIO, ContentType.VIDEO, ContentType.TEXT}
    ))
async def edit_test(update : types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        data = await state.get_data()
        course = await db.get_course(id = data['course_id'])
        button = await db.get_course_button(id = data['button_id'])
        await state.set_state(AdminTestBlock.main)
        await update.answer(f"Test blog: {button.name}", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))
    
    async with sema:
        current = await state.get_state()
        if current != AdminTestBlock.edit_test.state:
            return
        data = await state.get_data()
        media = data.get('media')

        if update.text and update.text.startswith('/undo'):
            if media:
                await state.update_data(media = None)
                await update.answer("✅ Xabar olib tashlandi", reply_markup=KeyboardManger.make_quiz())
            else:
                await update.answer("❗️ Media xabar topilmadi", reply_markup=KeyboardManger.make_quiz())

        elif media:
            await update.answer("❗️ Bu savoldan oldin faqat matn va mediafayl bilan bitta xabar koʻrsatilishi mumkin")
        else:
            await update.reply("Qoyilmaqom! Endi menga bu xabarga aloqador savolni yuborish uchun tugmadan foydalaning. \n\nAgar xabarni xatolik sababli yuborgan boʻlsangiz, orqaga qaytish uchun /undo buyrugʻini yuboring.")

            m = await update.copy_to(db.DATA_CHANEL_ID)
            await state.update_data(media = m.message_id)


@r.message(AdminTestBlock.edit_test, F.poll)
async def edit_test(update : types.Message, state: FSMContext):
    async with sema:
        poll = update.poll
        data = await state.get_data()
        media = data.get('media')
        course = await db.get_course(id = data.get('course_id'))
        button = await db.get_course_button(id = data.get('button_id'))
        test_id = data['test_id']
        test = await db.get_test(test_id)
    
        options = [option.text for option in poll.options]
        correct = options[poll.correct_option_id]
        options.remove(correct)
        options.insert(0, correct)

        await db.update_test(test.id, info = poll.explanation, question = poll.question, options = options, media = media)

        await state.set_state(AdminTestBlock.main)
        await update.answer("✅ Test muvaffaqiyatli o'zgartirildi", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))


@r.callback_query(AdminTestBlock.main, F.data.startswith('delete_'))
async def delete_test(update: types.CallbackQuery, state: FSMContext):
    test_id = int(update.data.replace('delete_', ''))
    test = await db.get_test(test_id)
    
    if test:
        data = await state.get_data()
        delete_test = data.get('delete_test')
        if delete_test == update.message.message_id:
            await db.delete_test(test_id)
            await update.message.answer("👍 Test muvaffaqiyatli o'chirildi")
            if can_edit(update.message.date):
                await update.message.delete()
            
        else:
            await state.update_data(delete_test = update.message.message_id)
            await update.answer("❗️ Ushbu testni o'chirish uchun tugmani yana bir marta bosing", show_alert=True, cache_time=1)
    else:
        await update.answer("❗️ Test topilmadi", show_alert=True)


@r.callback_query(AdminTestBlock.main, F.data.startswith('page_'))
async def paginator_handler(update: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    course_id = data.get('course_id')
    button_id = data.get('button_id')
    course = await db.get_course(id = course_id)
    button = await db.get_course_button(id = button_id)
    tests = await db.get_tests(course_button_id=button_id)
    tests_len = len(tests)

    page = int(update.data.replace('page_', ''))
    per_page = 10
    replay_markup = InlineKeyboardManager.tests_paginator(tests, per_page = per_page, page = page)
    if replay_markup:
        text = f"{per_page*page+1}/{per_page*page+per_page} dan {tests_len}  Testlar:"
        for test in tests[per_page*page : per_page*page+per_page]:
            text += f"\n{tests.index(test)+1}. {test.question}"

        await update.message.edit_text(text, reply_markup=InlineKeyboardManager.tests_paginator(tests, per_page = per_page, page = page))
    else:
        await update.answer("❗️ Boshqa sahifa yo'q", show_alert=True)



@r.callback_query(AdminTestBlock.main, F.data.startswith('test_'))
async def show_test(update: types.CallbackQuery, state: FSMContext):
    test_id = int(update.data.replace('test_', ''))
    test = await db.get_test(test_id)
    if not test:
        await update.answer("❗️ Test topilmadi", show_alert=True)
        return
    tests = await db.get_tests(course_button_id=test.courses_button)

    if update.message.poll and can_edit(update.message.date):
        try:
            await update.message.delete()
        except:
            pass

    prev = None
    next = None
    for test in tests:
        if test.id == test_id:
            if tests.index(test) > 0:
                prev = tests[tests.index(test)-1].id
            if tests.index(test) < len(tests)-1:
                next = tests[tests.index(test)+1].id
            break
    
    index = tests.index(test)
    await update.message.answer_poll(question=f"[{index+1}/{len(tests)}] {test.safe_question}", 
                                     options=test.options, 
                                     correct_option_id=0, 
                                     explanation=test.info, 
                                     is_anonymous=False, 
                                     is_closed=True,
                                     type='quiz',
                                     reply_markup=InlineKeyboardManager.test_edit_button(test, next=next, prev=prev))


@r.message(AdminTestBlock.get_test, F.content_type.in_(
        {ContentType.PHOTO, ContentType.VOICE, ContentType.AUDIO, ContentType.VIDEO, ContentType.TEXT}
    ))
async def get_test(update : types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        data = await state.get_data()
        course = await db.get_course(id = data['course_id'])
        button = await db.get_course_button(id = data['button_id'])
        await state.set_state(AdminTestBlock.main)
        await update.answer(f"Test blog: {button.name}", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))
    
    async with sema:
        current = await state.get_state()
        if current != AdminTestBlock.get_test.state:
            return
        data = await state.get_data()
        media = data.get('media')

        if update.text and update.text.startswith('/undo'):
            if media:
                await state.update_data(media = None)
                await update.answer("✅ Xabar olib tashlandi", reply_markup=KeyboardManger.make_quiz())
            else:
                await update.answer("❗️ Media xabar topilmadi", reply_markup=KeyboardManger.make_quiz())

        elif media:
            await update.answer("❗️ Bu savoldan oldin faqat matn va mediafayl bilan bitta xabar koʻrsatilishi mumkin")
        else:
            await update.reply("Qoyilmaqom! Endi menga bu xabarga aloqador savolni yuborish uchun tugmadan foydalaning. \n\nAgar xabarni xatolik sababli yuborgan boʻlsangiz, orqaga qaytish uchun /undo buyrugʻini yuboring.")

            m = await update.copy_to(db.DATA_CHANEL_ID)
            await state.update_data(media = m.message_id)

@r.message(AdminTestBlock.get_test, F.poll)
async def get_test(update : types.Message, state: FSMContext):
    async with sema:
        poll = update.poll
        data = await state.get_data()
        media = data.get('media')
        course = await db.get_course(id = data.get('course_id'))
        button = await db.get_course_button(id = data.get('button_id'))
    
        options = [option.text for option in poll.options]
        correct = options[poll.correct_option_id]
        options.remove(correct)
        options.insert(0, correct)

        test = Test(courses_button=button.id, question=poll.question, media=media, options=options, info=poll.explanation)
        await db.add_test(test)

        tests = await db.get_tests(course_button_id=button.id)
        await update.answer(f"✅ {len(tests)}-test qo'shildi")

        await update.answer(f"🧪 Menga {len(tests)+1}-savolingiz bilan soʻrovnoma yuboring. Bunga muqobil ravishda, bu savoldan oldin koʻrsatiladigan matn yoki mediafayl bilan xabar yuborishingiz mumkin.", 
                            reply_markup=KeyboardManger.make_quiz())
        await state.update_data(media = None)

