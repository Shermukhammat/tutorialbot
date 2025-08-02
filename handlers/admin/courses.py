from aiogram import Router, Dispatcher, types, F
from states import AdminPanel, AdminCourseMneu
from loader import db, dp
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import Semaphore
from data import Course
from utils.mytime import can_edit
from .main import r, sema, back_to_course_menu
from aiogram.types import ContentType


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
    
    # elif update.text == "➕ Test":
    #     await state.set_state(AdminPanel.add_course_button)
    #     await update.answer("✍️ Test nomini kirting", reply_markup=KeyboardManger.back())

    # elif update.text == "➕ Media":
    #     await state.set_state(AdminPanel.add_course_button)
    #     await update.answer("✍️ Media nomini kirting", reply_markup=KeyboardManger.back())

    # elif update.text == "➕ Menu":
    #     await state.set_state(AdminPanel.add_course_button)
    #     await update.answer("✍️ Menyu nomini kirting", reply_markup=KeyboardManger.back())

    else:
        data = await state.get_data()
        course_id = data.get('course_id')
        replay_markup = KeyboardManger.course_admin_menu(await db.get_course_buttons(course_id))
        await update.answer("❗️ Nomalum buyruq", reply_markup = replay_markup)



# @r.message(AdminCourseMneu.)
# async def get_course_button_name(update: types.Message, state: FSMContext):
#     if update.text == "⬅️ Orqaga":
#         data = await state.get_data()
#         course_id = data.get('course_id')
#         replay_markup = KeyboardManger.course_admin_menu(await db.get_course_buttons(course_id))
#         await update.answer("❗️ Nomalum buyruq", reply_markup = replay_markup)