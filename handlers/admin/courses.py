from aiogram import Router, Dispatcher, types, F
from states import AdminPanel, AdminCourseMneu, AdminCourseButton, AdminTestBlock, AdminMedia
from loader import db, dp, bot
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import Semaphore
from data import Course, CourseButtonType, Subscription
from utils.mytime import can_edit
from .main import r, sema, back_to_course_menu
from aiogram.types import ContentType
from uuid import uuid4



@r.callback_query(AdminCourseMneu.main, F.data.startswith('subnext_'))
async def course_users_paginator(update: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    course = await db.get_course(id = data['course_id'])

    if course:
        offset = int(update.data.replace('subnext_', ''))
        subs = await db.get_course_subs(course.id, offset = offset)
        leng = await db.course_sub_count(course.id)
        if subs:
            text = f"{course.name} foydlanuvchilari \n{offset+1 if offset else 1}-{len(subs)+offset} {leng} dan \n"
            for index, sub in enumerate(subs):
                text += f"\n{index+1}. {sub.full_name} {sub.created_at_readble} {sub.phone_number}"

            await update.message.edit_text(text, reply_markup=InlineKeyboardManager.course_users_paginator(subs, leng = leng, offset = offset))

@r.callback_query(AdminCourseMneu.main, F.data.startswith('sub_'))
async def show_subscriber_user(update: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    course = await db.get_course(id = data['course_id'])
    sub_id = int(update.data.replace('sub_', ''))
    sub = await db.get_subscribtion(id = sub_id)
    if sub and sub.user_id:
        user = await db.get_user(sub.user_id)
        await update.message.answer(f"👤 Foydalanuvchi: {user.fullname} \n📱 Telefon raqami: {user.phone_number} \n📬 Username: {user.fixsed_username} \n🗓 Ro'yxatdan o'tdi: {user.registred_readble}  \n👑 Oubuna bo'ldi: {sub.created_at_readble}",
                                    reply_markup=InlineKeyboardManager.delete_user_sub(sub.id))

    elif sub:
        await update.message.answer(f"👤 Foydalanuvchi: Kutilmoqda \n👑 Oubuna bo'ldi: {sub.created_at_readble}",
                                    reply_markup=InlineKeyboardManager.delete_user_sub(sub.id))
    else:
        await update.answer("❗️Bunday foydalanuvchi topilmadi", show_alert=True)

@r.callback_query(AdminCourseMneu.main, F.data.startswith('delete_sub_'))
async def delete_sub_handler(update: types.CallbackQuery, state: FSMContext):
    sub_id = int(update.data.replace('delete_sub_', ''))
    sub = await db.get_subscribtion(id = sub_id)
    data = await state.get_data()
    delete_sub_message_id = data.get('delete_sub_message_id')
    if sub:
        if delete_sub_message_id == update.message.message_id:
            await db.delete_subscribtion(sub.id)
            await update.answer("✅ Obuna o'chirildi", show_alert=True)
            await update.message.delete()
        else:
            await state.update_data(delete_sub_message_id = update.message.message_id)
            await update.answer(f"⚠️ Obunani o'chirish uchun ushbu tugmani 3 sonyadan keyin yana bosing", show_alert=True, cache_time=3)
        
@r.callback_query(AdminCourseMneu.main)
async def callback_course_menu_wrapper(update: types.CallbackQuery, state: FSMContext):
    async with sema:
        return await callback_course_menu(update, state)
    
async def callback_course_menu(update: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if update.message.message_id != data.get('message_id'):
        await update.answer("❗️ Nomalum buyruq", show_alert=True)
        return
    
    course = await db.get_course(id = data['course_id'])
    if update.data == 'pro':
        await db.update_course(course.id, pro = not course.pro)

        if course.pro:
            await update.answer("🆓 Kurs endi tekin", show_alert=True)
        else:
            await update.answer("👑 Kurs endi pullik", show_alert=True)
        
        course.pro = not course.pro
        reply_markup = InlineKeyboardManager.edit_course(course)
        if can_edit(update.message.date):
            await update.message.edit_reply_markup(reply_markup=reply_markup)
    
    elif update.data == 'new_line':
        await db.update_course(course.id, new_line = not course.new_line)

        if course.new_line:
            await update.answer("❌ Tugmadan oldin yangi qator tashlanmaydi", show_alert=True)
        else:
            await update.answer("🆕 Tugmadan oldin yangi qator tashlandai", show_alert=True)
        
        course.new_line = not course.new_line
        reply_markup = InlineKeyboardManager.edit_course(course)
        if can_edit(update.message.date):
            await update.message.edit_reply_markup(reply_markup=reply_markup)

    elif update.data == 'edit_name':
        await state.set_state(AdminCourseMneu.edit_name)
        await update.message.answer(f"✍️ {course.name} kursi uchun yangi nom kiriting", reply_markup=KeyboardManger.back())
    
    elif update.data == 'edit_media':
        await state.set_state(AdminCourseMneu.edit_media)
        await update.message.answer(f"💰 {course.name} kursi uchun sotib olish xabarni kirting video, rasm yoki tekst holatida", reply_markup=KeyboardManger.back())

    elif update.data == 'delete':
        await state.set_state(AdminCourseMneu.delete1)
        await update.message.answer(f"☠️")
        await update.message.answer(f"{course.name} kursni o'chirmoqchimisiz?", reply_markup=KeyboardManger.yes1())


@r.message(AdminCourseMneu.delete1)
async def delete_course(update: types.Message, state: FSMContext):
    if update.text == "Xa":
        await state.set_state(AdminCourseMneu.delete2)
        data = await state.get_data()
        course = await db.get_course(id = data['course_id'])
        await update.answer(f"Aniq {course.name} kursni o'chirmoqchimszi? \n❗️ Keyin kurs malumtlarni qayta tiklab bo'lmaydi",
                            reply_markup=KeyboardManger.yes2())
    else:
        await back_to_course_menu(update, state)


@r.message(AdminCourseMneu.delete2)
async def delete_course(update: types.Message, state: FSMContext):
    if update.text == "Xa 100%":
        data = await state.get_data()
        course = await db.get_course(id = data['course_id'])
        await db.delete_course(id = course.id)
        await update.answer(f"✅ {course.name} kurs o'chirildi")
        
        await state.set_state(AdminPanel.main)
        await update.answer("🎛 Admin panel", reply_markup=KeyboardManger.panel(await db.get_courses()))
    else:
        await back_to_course_menu(update, state)


@r.message(AdminCourseMneu.edit_name)
async def edit_course_name(update : types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await back_to_course_menu(update, state)
    
    elif len(update.text) <= 35:
        async with sema:
            if len(await db.get_courses(use_cache=False)) > 45:
                await update.answer("❗️ 45 tadan ko'p kurs qoshish mumkun emas", reply_markup = KeyboardManger.back())
            elif await db.get_course(name = update.text):
                await update.answer("❗️ Bunday kurs mavjud", reply_markup = KeyboardManger.back())
            else:
                data = await state.get_data()
                course = await db.get_course(id = data['course_id'])
                await db.update_course(course.id, name = update.text)
                await back_to_course_menu(update, state)
 
    else:
        await update.reply("❗️ Kurs nomi 35 ta belgidan ko'p bo'lmasligi kerak", reply_markup=KeyboardManger.back())
        

@r.message(AdminCourseMneu.edit_media, F.content_type.in_(
        {ContentType.PHOTO, ContentType.VIDEO, ContentType.TEXT}
    ))
async def edit_course_media(update : types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await back_to_course_menu(update, state)
        return 
    
    data = await state.get_data()
    course = await db.get_course(id = data['course_id'])
    m = await update.copy_to(db.DATA_CHANEL_ID)
    await db.update_course(course.id, message = m.message_id)

    await update.answer("✅ Kurs xabari yangilandi")
    await back_to_course_menu(update, state)


@r.message(AdminCourseMneu.main)
async def course_menu(update : types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.set_state(AdminPanel.main)
        await update.answer("🎛 Admin panel", reply_markup=KeyboardManger.panel(await db.get_courses()))
    
    elif update.text == "➕ Test blok":
        await state.set_state(AdminCourseButton.add)
        await state.update_data(type = CourseButtonType.TEST)
        await update.answer("📦 Test bolgi nomini kirting", reply_markup=KeyboardManger.back())

    elif update.text == "➕ Media":
        await state.set_state(AdminCourseButton.add)
        await state.update_data(type = CourseButtonType.MEDIA)
        await update.answer("📁 Media tugmasi nomini kirting", reply_markup=KeyboardManger.back())

    # elif update.text == "➕ Menu":
    #     await state.set_state(AdminCourseButton.add)
    #     await state.update_data(type = CourseButtonType.INNER_MENU)
    #     await update.answer("🎛 Menyu tugmasi nomini kirting", reply_markup=KeyboardManger.back())

    elif update.text == "➕ Foydalnuvchi":
        async with sema:
            data = await state.get_data()
            course = await db.get_course(data.get('course_id'))
            sub = Subscription(token=uuid4().hex, course=course.id)
            for _ in range(3):
                if await db.get_subscribtion(token = sub.token):
                    sub.token = uuid4().hex
                    continue
                
                await db.add_subscribtion(sub)
                await update.answer(f"{course.name} kursi uchun obunani folashtirish uchun pastdagi tugmani bosing 👇",
                                    reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                        [types.InlineKeyboardButton(text="👑 Folashtirish", url = f"https://t.me/{db.bot.username}?start={sub.token}")]
                                        ]))
                break

    elif update.text == "🧹 Foydalnuvchilarni tozlash":
        data = await state.get_data()
        course = await db.get_course(data.get('course_id'))
        if course:
            await state.set_state(AdminCourseMneu.clear_subs_1)
            await update.answer(f"⚠️ Xaqiqatdan ham {course.name} kursi foydalanuvchilari obunalarni o'chirmoqchimisiz?",
                                reply_markup=KeyboardManger.yes1())
    
    elif update.text == '🎓 Foydalnuvchilar':
        data = await state.get_data()
        course = await db.get_course(data.get('course_id'))
        if course:
            leng = await db.course_sub_count(course.id)
            subs = await db.get_course_subs(course.id)
            text = f"{course.name} foydlanuvchilari \n1-{len(subs)} {leng} dan \n"
            for index, sub in enumerate(subs):
                text += f"\n{index+1}. {sub.full_name} {sub.created_at_readble} {sub.phone_number}"

            await update.answer(text, reply_markup=InlineKeyboardManager.course_users_paginator(subs, leng = leng))

    else:
        data = await state.get_data()
        course_id = data.get('course_id')
        course = await db.get_course(id = course_id)
        button = await db.get_course_button(course_id = course_id, name = update.text)

        if button:
            if button.type == CourseButtonType.TEST:
                await state.set_state(AdminTestBlock.main)
                await state.update_data(button_id = button.id)
                await update.answer(f"Test blog: {button.name}", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))
                
            elif button.type == CourseButtonType.MEDIA:
                await state.set_state(AdminMedia.main)
                await state.update_data(button_id = button.id)
                await update.answer(f"Media: {button.name}", reply_markup=KeyboardManger.edit_course_button(button, pro=course.pro))

            elif button.type == CourseButtonType.INNER_MENU:
                await update.answer(f"Menyu: {button.name}")
        else:
            replay_markup = KeyboardManger.course_admin_menu(await db.get_course_buttons(course_id), pro = course.pro)
            await update.answer("❗️ Nomalum buyruq", reply_markup = replay_markup)



@r.message(AdminCourseMneu.clear_subs_1)
async def clear_sub_1(update: types.Message, state: FSMContext):
    if update.text == "Xa":
        data = await state.get_data()
        course_id = data.get('course_id')
        course = await db.get_course(id = course_id)
        if course:
            await state.set_state(AdminCourseMneu.clear_subs_2)
            await update.answer("☠️")
            await update.answer(f"⚠️ Aniq {course.name} kursi barcha obunlarni o'chirmoqchimisiz? ❗️ Keyin kurs obunalarni qayta tiklab bo'lmaydi", reply_markup=KeyboardManger.yes2()) 

    else:
        await back_to_course_menu(update, state)


@r.message(AdminCourseMneu.clear_subs_2)
async def clear_sub_2(update: types.Message, state: FSMContext):
    if update.text == "Xa 100%":
        data = await state.get_data()
        course_id = data.get('course_id')
        course = await db.get_course(id = course_id)
        if course:
            await db.clear_course_subs(course_id)
            await update.answer("✅ Obunalar o'chirildi")
            await back_to_course_menu(update, state)
    else:
        await back_to_course_menu(update, state)
