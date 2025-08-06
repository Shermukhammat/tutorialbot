from aiogram import Router, Dispatcher, types, F
from states import AdminPanel, AdminCourseMneu
from loader import db, dp
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import Semaphore
from data import Course
from utils.mytime import can_edit

r = Router()
dp.include_router(r)
sema = Semaphore()


@r.message(AdminPanel.main)
async def main_handler(update : types.Message, state: FSMContext):
    if update.text == "⬅️ Chiqish":
        await state.clear()
        subs = [sub.course for sub in await db.get_subscribtions(update.from_user.id)]
        await update.answer("🏠 Bosh menyu", reply_markup=KeyboardManger.home(await db.get_courses(), subs = subs))
        return
    
    elif update.text == "➕ Kurs qo'shish":
        await state.set_state(state = AdminPanel.add_course)
        await update.answer("👌 Yaxshi, yangi kurs nomini kiriting", reply_markup = KeyboardManger.back())
        return
    

    course = await db.get_course(name=update.text)
    if course:
        await state.set_state(AdminCourseMneu.main)
        await state.update_data(course_id = course.id)
        
        reply_markup = KeyboardManger.course_admin_menu(await db.get_course_buttons(course.id), pro = course.pro)
        await update.answer("📚", reply_markup=reply_markup)
        reply_markup = InlineKeyboardManager.edit_course(course)
        message = await update.answer(f"{course.name} kursi", reply_markup=reply_markup)
        await state.update_data(message_id = message.message_id)
    else:
        await update.answer("❗️ Nomalum buyruq", reply_markup=KeyboardManger.panel(await db.get_courses()))




async def back_to_course_menu(update: types.Message, state: FSMContext):
    data = await state.get_data()
    course = await db.get_course(id=data.get('course_id'))

    if course:
        await state.set_state(AdminCourseMneu.main)
        await state.update_data(course_id = course.id)
        
        reply_markup = KeyboardManger.course_admin_menu(await db.get_course_buttons(course.id), pro = course.pro)
        await update.answer("📚", reply_markup=reply_markup)
        reply_markup = InlineKeyboardManager.edit_course(course)
        message = await update.answer(f"{course.name} kursi", reply_markup=reply_markup)
        await state.update_data(message_id = message.message_id)
    else:
        await state.set_state(AdminPanel.main)
        await update.answer("🎛 Admin panel", reply_markup=KeyboardManger.panel(await db.get_courses()))


@r.message(AdminPanel.edit_course_name)
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
                await db.add_course(Course(name=update.text))
                await back_to_course_menu(update, state)
 
    else:
        await update.reply("❗️ Kurs nomi 35 ta belgidan ko'p bo'lmasligi kerak", reply_markup=KeyboardManger.back())
        

@r.message(AdminPanel.add_course)
async def add_course(update : types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.set_state(AdminPanel.main)
        await update.answer("🎛 Admin panel", reply_markup=KeyboardManger.panel(await db.get_courses()))

    elif len(update.text) <= 35:
        async with sema:
            if len(await db.get_courses(use_cache=False)) > 45:
                await update.answer("❗️ 45 tadan ko'p kurs qoshish mumkun emas", reply_markup = KeyboardManger.back())
            elif await db.get_course(name = update.text):
                await update.answer("❗️ Bunday kurs mavjud", reply_markup = KeyboardManger.back())
            else:
                await db.add_course(Course(name=update.text))
                await state.set_state(AdminPanel.main)
                await update.answer("✅ Kurs qo'shildi", reply_markup = KeyboardManger.panel(await db.get_courses()))
 
    else:
        await update.reply("❗️ Kurs nomi 35 ta belgidan ko'p bo'lmasligi kerak", reply_markup=KeyboardManger.back())
