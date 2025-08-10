from aiogram import Router, Dispatcher, types, F
from states import AdminPanel, AdminCourseMneu, AdminCourseButton, AdminTestBlock, AdminInnerMedia, AdminInnerMenu
from loader import db, dp, bot
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import Semaphore
from data import Course, CourseButtonType, Subscription
from utils.mytime import can_edit
from .main import r, sema, back_to_course_menu
from aiogram.types import ContentType
from uuid import uuid4

async def back_to_inner_menu_editor(update: types.Message, state: FSMContext):
    data = await state.get_data()
    course = await db.get_course(id = data.get('course_id'))
    button = await db.get_course_button(id = data.get('button_id'))
    inner_buttons = await db.get_course_inner_buttons(button.id)
    replay_markup = KeyboardManger.edit_inner_menu(inner_buttons, button, pro = course.pro)
    
    await state.set_state(AdminInnerMenu.main)
    await update.answer(f"Menyu: {button.name}", reply_markup=replay_markup)


@r.message(AdminInnerMedia.main)
async def admin_media_menu(update: types.Message, state: FSMContext):
    data = await state.get_data()
    button = await db.get_course_button(id = data['button_id'])
    course = await db.get_course(id = button.course)
    inner_button = await db.get_course_inner_button(id = data.get('inner_button_id'))

    if update.text == "⬅️ Orqaga":
        await back_to_inner_menu_editor(update, state)

    elif update.text == '🔄 Mediani yangilash':
        await state.set_state(AdminInnerMedia.get_media)
        await state.update_data(media = [])
        await update.answer("⬆️ Yangi medilarni yuboring va saqlash tugmasni bosing", reply_markup=KeyboardManger.media_saver())

    elif update.text == '📁 Media':
        if inner_button.media:
            await bot.copy_messages(chat_id=update.chat.id, from_chat_id=db.DATA_CHANEL_ID, message_ids=inner_button.media)
        else:
            await update.answer_sticker("CAACAgIAAxkBAAIHbGiPFIlhq8G6gLcKvA-jWf1yz2kIAAL5AANWnb0KlWVuqyorGzY2BA")
            await update.answer(f"Birotaham media yo'q", reply_markup=KeyboardManger.inner_button(inner_button, pro=course.pro)) 
        
    elif update.text == "✅ Qator tashla":
        await db.update_course_inner_button(id = inner_button.id, new_line = False)
        inner_button.new_line = False
        await update.answer("✅ Endi tugmadan oldin yangi qator tashlanmaydi", reply_markup=KeyboardManger.edit_inner_button(inner_button, pro=course.pro))

    elif update.text == "❌ Qator tashla":
        await db.update_course_inner_button(id = inner_button.id, new_line = True)
        inner_button.new_line = True
        await update.answer("✅ Endi tugmadan oldin yangi qator tashlanadi", reply_markup=KeyboardManger.edit_inner_button(inner_button, pro=course.pro))

    elif update.text == "🔒 Yopiq":
        await db.update_course_inner_button(id = inner_button.id, open = True)
        inner_button.open = True
        await update.answer("✅ Endi media tugmasidan obuna bo'lmasdan foydalanish mumkin", reply_markup=KeyboardManger.edit_inner_button(inner_button, pro=course.pro))

    elif update.text == "🔓 Ochiq":
        await db.update_course_inner_button(id = inner_button.id, open = False)
        inner_button.open = False
        await update.answer("✅ Endi media tugmasidan obuna bo'lmasdan foydalanish mumkin emas", reply_markup=KeyboardManger.edit_inner_button(inner_button, pro=course.pro))

    elif update.text == "✏️ Nomi":
        await state.set_state(AdminInnerMedia.rename)
        await update.answer(f"{inner_button.name} tugmasni yangi nomini kirting ✍️",
                            reply_markup=KeyboardManger.back())

    elif update.text == "🗑 O'chirish":
        await state.set_state(AdminInnerMedia.delete)
        await update.answer(f"⚠️ {inner_button.name} tugmasni o'chirishni xoxlaysizmi?",
                            reply_markup=KeyboardManger.yes_or_no())

    else:
        await update.answer(f"Media tugma: {inner_button.name}", reply_markup=KeyboardManger.edit_inner_button(inner_button, pro=course.pro)) 


@r.message(AdminInnerMedia.delete)
async def delete_media_button(update: types.Message, state: FSMContext):
    data = await state.get_data()
    button = await db.get_course_button(id = data['button_id'])
    course = await db.get_course(id = button.course)
    inner_button = await db.get_course_inner_button(id = data.get('inner_button_id'))

    if update.text == "✅ Xa":
        await db.delete_course_inner_button(inner_button.id)
        await update.answer("✅ Tugma o'chirildi")
        await back_to_inner_menu_editor(update, state)
    
    else:
        await state.set_state(AdminInnerMedia.main)
        await update.answer(f"Media tugma: {inner_button.name}", reply_markup=KeyboardManger.edit_inner_button(inner_button, pro=course.pro))


@r.message(AdminInnerMedia.rename)
async def rename_button(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        data = await state.get_data()
        button = await db.get_course_button(id = data['button_id'])
        course = await db.get_course(id = button.course)
        inner_button = await db.get_course_inner_button(id = data.get('inner_button_id'))
        await state.set_state(AdminInnerMedia.main)
        await update.answer(f"Media tugma: {inner_button.name}", reply_markup=KeyboardManger.edit_inner_button(inner_button, pro=course.pro))
    else:
        async with sema:
            data = await state.get_data()
            button = await db.get_course_button(id = data['button_id'])
            course = await db.get_course(id = button.course)
            buttons = await db.get_course_inner_buttons(button.id)
            inner_button = await db.get_course_inner_button(id = data.get('inner_button_id'))
            
            if update.text in [bt.name for bt in buttons]:
                await update.answer(f"❗️ Bunday tugma mavjud", reply_markup=KeyboardManger.back())
            else:
                await db.update_course_inner_button(inner_button.id, name = update.text)
                await state.set_state(AdminInnerMedia.main)
                await update.answer(f"✅ Tugma nomi yangilandi", reply_markup=KeyboardManger.edit_inner_button(inner_button, pro=course.pro))
            


@r.message(AdminInnerMedia.get_media, F.content_type.in_(
        {ContentType.PHOTO, ContentType.VIDEO, ContentType.DOCUMENT, ContentType.AUDIO, ContentType.VOICE, ContentType.TEXT}
    ))
async def get_media(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        data = await state.get_data()
        button = await db.get_course_button(id = data['button_id'])
        course = await db.get_course(id = button.course)
        inner_button = await db.get_course_inner_button(id = data.get('inner_button_id'))
        await state.set_state(AdminInnerMedia.main)
        await update.answer(f"Media: {inner_button.name}", reply_markup=KeyboardManger.edit_inner_button(inner_button, pro=course.pro))
    
    elif update.text == "✅ Saqlash":
        data = await state.get_data()
        media = data.get('media', [])
        if not media:
            return await update.answer("❗️ Kamida 1ta media yuboring", reply_markup=KeyboardManger.media_saver())
        
        button = await db.get_course_button(id = data['button_id'])
        course = await db.get_course(id = button.course)
        inner_button = await db.get_course_inner_button(id = data.get('inner_button_id'))
        
        await db.update_course_inner_button(inner_button.id, media = media)
        await state.set_state(AdminInnerMedia.main)
        await update.answer(f"✅ Medialar yangilandi", reply_markup=KeyboardManger.edit_inner_button(inner_button, pro=course.pro)) 

    else:
        data = await state.get_data()
        media : list[int] = data.get('media', [])
        if len(media) > 50:
            return await update.answer("❗️ 50 tadan kop media yuborishingiz mumkun emas", 
                                reply_markup=KeyboardManger.media_saver(save=True))
        
        m = await update.copy_to(db.DATA_CHANEL_ID)
        media.append(m.message_id)
        await state.update_data(media = media)
        await update.react([types.ReactionTypeEmoji(emoji="👍")])

        if len(media) == 1:
            await update.answer("✅ Median saqlashingiz yoki yana 49 ta media yuborishingiz mumkun", 
                                reply_markup=KeyboardManger.media_saver(save=True))