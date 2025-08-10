from aiogram import Router, Dispatcher, types, F
from states import AdminPanel, AdminCourseMneu, AdminCourseButton, AdminTestBlock, AdminMedia, Settings, AdsMenu, AdminInnerMenu, AdminInnerTestBlock
from loader import db, dp, bot
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import Semaphore
from data import Course, CourseButtonType, Subscription, Chanel, User, CourseInnerButton
from utils.mytime import can_edit
from .main import r, back_to_course_menu
from aiogram.types import ContentType
from uuid import uuid4
from aiogram.enums import ParseMode
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner



sema = Semaphore()

@r.message(AdminInnerMenu.main)
async def inner_menu_editor(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await back_to_course_menu(update, state)
        return
    
    data = await state.get_data()
    course = await db.get_course(id = data.get('course_id'))
    button = await db.get_course_button(id = data.get('button_id'))
    inner_buttons = await db.get_course_inner_buttons(button.id)
    replay_markup = KeyboardManger.edit_inner_menu(inner_buttons, button, pro = course.pro)
    
    if update.text == "✏️ Nomi":
        await state.set_state(AdminInnerMenu.update_name)
        await update.answer("Menyuning yangi nomini kirting", reply_markup=KeyboardManger.back())

    elif update.text == "🗑 O'chirish":
        await state.set_state(AdminInnerMenu.delete1)
        await update.answer("☠️")
        await update.answer(f"Menyuni o'chirmoqchimisiz?", reply_markup=KeyboardManger.yes1())

    elif update.text == "🔒 Yopiq":
        await db.update_course_button(button.id, open = True)
        button.open = True
        await update.answer("✅ Menyudan endi obuna bo'lmasdan foydlanish mumkun", reply_markup=KeyboardManger.edit_inner_menu(inner_buttons, button, pro = course.pro))

    elif update.text == "🔓 Ochiq":
        await db.update_course_button(button.id, open = False)
        button.open = False
        await update.answer("✅ Menyudan endi obuna bo'lmasdan foydlanish mumkun emas", reply_markup=KeyboardManger.edit_inner_menu(inner_buttons, button, pro = course.pro))

    elif update.text == "❌ Qator tashla":
        await db.update_course_button(button.id, new_line = True)
        button.new_line = True
        await update.answer("✅ Menyudan oldin yangi qator tashlanadi", reply_markup=KeyboardManger.edit_inner_menu(inner_buttons, button, pro = course.pro))

    elif update.text == "✅ Qator tashla":
        await db.update_course_button(button.id, new_line = False)
        button.new_line = False
        await update.answer("✅ Menyudan oldin yangi qator tashlanmaydi", reply_markup=KeyboardManger.edit_inner_menu(inner_buttons, button, pro = course.pro))

    elif update.text == "➕ test blok":
        await state.set_state(AdminInnerMenu.add_button)
        await state.update_data(type = 'test')
        await update.answer("Test blokni nomini kirting", reply_markup=KeyboardManger.back())

    elif update.text == "➕ media":
        await state.set_state(AdminInnerMenu.add_button)
        await state.update_data(type = 'media')
        await update.answer("Media tugma nomini kirting", reply_markup=KeyboardManger.back())

    else:
        inner_button = await db.get_course_inner_button(name=update.text, course_button=button.id)
        if inner_button:
            if inner_button.type == CourseButtonType.TEST:
                await state.set_state(AdminInnerTestBlock.main)
                await state.update_data(inner_button_id = inner_button.id)
                await update.answer(f"{inner_button.name} test blog", reply_markup=KeyboardManger.edit_inner_button(inner_button, pro = course.pro))
            else:
                await update.answer("Bu media tugma", reply_markup=replay_markup)
        else:
            await update.answer("❗️ Nomalum buyruq", reply_markup=replay_markup)


@r.message(AdminInnerMenu.update_name)
async def update_inner_menu_name(update: types.Message, state: FSMContext):
    data = await state.get_data()
    course = await db.get_course(id = data.get('course_id'))
    button = await db.get_course_button(id = data.get('button_id'))
    inner_buttons = await db.get_course_inner_buttons(button.id)
    replay_markup = KeyboardManger.edit_inner_menu(inner_buttons, button, pro = course.pro)

    if update.text == "⬅️ Orqaga":
        await state.set_state(AdminInnerMenu.main)
        await update.answer(f"Menyu: {button.name}", reply_markup=replay_markup)
    
    elif len(update.text) <= 35:
        async with sema:
            buttons = await db.get_course_buttons(course.id)
            if update.text in [b.name for b in buttons]:
                await update.answer("❗️ Bunday tugma nomi mavjud", reply_markup=KeyboardManger.back())
                return
            
            await db.update_course_button(button.id, name = update.text)
            await state.set_state(AdminInnerMenu.main)
            await update.answer(f"Menyu: {update.text}", reply_markup=replay_markup)


    else:
        await update.answer("❗️ Menyu nomi 35 ta belgidan ko'p bo'lmasligi kerak", reply_markup=KeyboardManger.back())



@r.message(AdminInnerMenu.delete1)
async def delete_inner_menu(update: types.Message, state: FSMContext):
    data = await state.get_data()
    course = await db.get_course(id = data.get('course_id'))
    button = await db.get_course_button(id = data.get('button_id'))
    if update.text == 'Xa':
        await state.set_state(AdminInnerMenu.delete2)
        await update.answer(f"Aniq {button.name} menyusini o'chirmoqchimisiz?", reply_markup=KeyboardManger.yes2())
    
    else:
        inner_buttons = await db.get_course_inner_buttons(button.id)
        replay_markup = KeyboardManger.edit_inner_menu(inner_buttons, button, pro = course.pro)
        await state.set_state(AdminInnerMenu.main)
        await update.answer(f"Menyu: {button.name}", reply_markup=replay_markup)


@r.message(AdminInnerMenu.delete2)
async def delete_inner_menu2(update: types.Message, state: FSMContext):
    data = await state.get_data()
    course = await db.get_course(id = data.get('course_id'))
    button = await db.get_course_button(id = data.get('button_id'))
    inner_buttons = await db.get_course_inner_buttons(button.id)
    replay_markup = KeyboardManger.edit_inner_menu(inner_buttons, button, pro = course.pro)
    await state.set_state(AdminInnerMenu.main)

    if update.text == 'Xa 100%':
        await db.delete_course_button(button.id)
        await update.answer(f"✅ Menyu o'chirildi")
        await back_to_course_menu(update, state)

    else:
        await update.answer(f"Menyu: {button.name}", reply_markup=replay_markup)


@r.message(AdminInnerMenu.add_button)
async def add_inner_button(update: types.Message, state: FSMContext):
    data = await state.get_data()
    course = await db.get_course(id = data.get('course_id'))
    button = await db.get_course_button(id = data.get('button_id'))
    inner_buttons = await db.get_course_inner_buttons(button.id)
    replay_markup = KeyboardManger.edit_inner_menu(inner_buttons, button, pro = course.pro)
    type = data.get('type', 'media')

    if update.text == "⬅️ Orqaga":
        await state.set_state(AdminInnerMenu.main)
        await update.answer(f"Menyu: {button.name}", reply_markup=replay_markup)
    
    elif len(update.text) <= 35:
        async with sema:
            inner_buttons = await db.get_course_inner_buttons(button.id)
            if update.text in [b.name for b in inner_buttons]:
                await update.answer("❗️ Bunday tugma nomi mavjud", reply_markup=KeyboardManger.back())
                return
            await state.set_state(AdminInnerMenu.main)
            inner_button = CourseInnerButton(name=update.text,
                                             course=button.course, 
                                             course_button=button.id, 
                                             type=CourseButtonType.TEST if type == 'test' else CourseButtonType.MEDIA)
            
            await db.add_course_inner_button(inner_button)
            inner_buttons = await db.get_course_inner_buttons(button.id)
            replay_markup = KeyboardManger.edit_inner_menu(inner_buttons, button, pro = course.pro)
            await update.answer(f"✅ Tugma qo'shildi", reply_markup=replay_markup)
    
    else:
        await update.answer("❗️ Nomi 35 ta belgidan ko'p bo'lmasligi kerak", reply_markup=KeyboardManger.back())
            

