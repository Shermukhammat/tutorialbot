from aiogram import Router, Dispatcher, types, F
from states import AdminPanel, AdminCourseMneu, AdminCourseButton
from loader import db, dp
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import Semaphore
from data import Course, CourseButton, CourseButtonType
from utils.mytime import can_edit
from .main import r, sema, back_to_course_menu
from aiogram.types import ContentType 


@r.message(AdminCourseButton.add)
async def add_test_button(update : types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await back_to_course_menu(update, state)
        return 
    
    async with sema:
        data = await state.get_data()
        type = data.get('type')
        course = await db.get_course(id = data['course_id'])
        buttons = await db.get_course_buttons(course.id, use_cache=False)

        if len(buttons) > 45:
            await update.answer("❗️ Kurs tugmalari soni 45 tadan ko'p bo'lmasligi kerak", reply_markup=KeyboardManger.back())
            return
        
        if update.text in [b.name for b in buttons]:
            await update.answer("❗️ Bunday tugma mavjud", reply_markup=KeyboardManger.back())
            return
        
        if len(update.text) > 35:
            await update.answer("❗️ Tugma nomi 35 ta belgidan ko'p bo'lmasligi kerak", reply_markup=KeyboardManger.back())
            return

    
        button = CourseButton(name=update.text, course=course.id, type=type)
        await db.add_course_button(button)
        
        if type == CourseButtonType.TEST:
            await update.answer("✅ Test blogi qo'shildi")
        elif type == CourseButtonType.MEDIA:
            await update.answer("✅ Media qo'shildi")
        elif type == CourseButtonType.INNER_MENU:
            await update.answer("✅ Menyu qo'shildi")
        
        await back_to_course_menu(update, state)