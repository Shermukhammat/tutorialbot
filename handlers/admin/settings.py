from aiogram import Router, Dispatcher, types, F
from states import AdminPanel, AdminCourseMneu, AdminCourseButton, AdminTestBlock, AdminMedia, Settings
from loader import db, dp, bot
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import Semaphore
from data import Course, CourseButtonType, Subscription
from utils.mytime import can_edit
from .main import r, sema, back_to_course_menu
from aiogram.types import ContentType
from uuid import uuid4




@r.callback_query(Settings.main, F.data == 'update_help')
async def update_help_content(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(Settings.update_help_content)
    await update.message.answer("⬆️ Yangi yordam kontentini kirting", reply_markup=KeyboardManger.back())



@r.message(Settings.update_help_content, F.content_type.in_(
        {ContentType.TEXT, ContentType.VIDEO, ContentType.PHOTO, ContentType.AUDIO, ContentType.DOCUMENT, ContentType.VOICE}
    ))
async def get_help_content(update: types.Message, state: FSMContext):
    await state.set_state(Settings.main)

    if update.text == "⬅️ Orqaga":
        await update.answer("Sozlamalar menyusi", reply_markup = KeyboardManger.settings())

    else:
        m = await update.copy_to(db.DATA_CHANEL_ID)
        db.HELP_CONTENT = m.message_id
        db.params_data['help_content'] = m.message_id
        await db.update_params()
        await update.answer("✅ Yordam kontenti yangilandi", reply_markup=KeyboardManger.settings())

@r.message(Settings.main)
async def settings_main(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.set_state(AdminPanel.main)
        await update.answer("🎛 Admin panel", reply_markup=KeyboardManger.panel(await db.get_courses()))
        
    
    elif update.text == "📖 Yordam kontenti":
        reply_markup=InlineKeyboardManager.update_button('update_help')
        if db.HELP_CONTENT:
            await bot.copy_message(chat_id=update.from_user.id,
                                    from_chat_id=db.DATA_CHANEL_ID,
                                    message_id=db.HELP_CONTENT,
                                    reply_markup=reply_markup)
        else:
            await update.answer("⚡️ Yordam ma'lumoti yuklanmagan", reply_markup=reply_markup)

    else:
        await update.answer("Sozlamalar menyusi", reply_markup=KeyboardManger.settings())
    
        