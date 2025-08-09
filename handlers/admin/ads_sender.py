from aiogram import Router, Dispatcher, types, F
from states import AdminPanel, AdminCourseMneu, AdminCourseButton, AdminTestBlock, AdminMedia, Settings, AdsMenu
from loader import db, dp, bot
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import Semaphore
from data import Course, CourseButtonType, Subscription, Chanel, User
from utils.mytime import can_edit
from .main import r, back_to_course_menu
from aiogram.types import ContentType
from uuid import uuid4
from aiogram.enums import ParseMode
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner



@r.message(AdsMenu.chose_courses)
async def chose_courses(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.clear()
        await state.set_state(AdminPanel.main)
        await update.answer("Admin panel", reply_markup=KeyboardManger.panel(await db.get_courses()))
        return
    
    elif update.text == "👥 Hammaga":
        await state.set_state(AdsMenu.get_media)
        await state.update_data(all = True)
        await update.answer("📁 Xabaringizni jonating video, tekst yoki rasim ko'rnishda",
                            reply_markup=KeyboardManger.back())
        return
    
    course = await db.get_course(name=update.text)
    if course:
        await state.set_state(AdsMenu.get_media)
        await state.update_data(course_id = course.id, all = False)
        await update.answer("📁 Xabaringizni jonating video, tekst yoki rasim ko'rnishda",
                            reply_markup=KeyboardManger.back())
        
    else:
        await update.answer("❗️ Bunday kurs mavjud emas", reply_markup=KeyboardManger.chose_courses_for_ads(await db.get_courses()))

    
@r.message(AdsMenu.get_media, F.content_type.in_({ContentType.TEXT, ContentType.VIDEO, ContentType.PHOTO, ContentType.DOCUMENT, ContentType.AUDIO, ContentType.VOICE}))
async def update_answer(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.clear()
        await state.set_state(AdsMenu.chose_courses)
        await update.answer("👇 Xabarni qaysi kursga jo'natishni tanlang", reply_markup=KeyboardManger.chose_courses_for_ads(await db.get_courses()))
    else:
        m = await update.copy_to(db.DATA_CHANEL_ID)
        await state.update_data(message_id = m.message_id)
        await state.set_state(AdsMenu.wana_add_button)
        await update.answer("🔘 Xabarga tugma qoshamizmi?", reply_markup=KeyboardManger.yes_or_no())



@r.message(AdsMenu.wana_add_button)
async def wana_add_button(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.set_state(AdsMenu.get_media)
        await update.answer("📁 Xabaringizni jonating video, tekst yoki rasim ko'rnishda",
                            reply_markup=KeyboardManger.back())
    
    elif update.text == "✅ Xa":
        await state.set_state(AdsMenu.get_button_name)
        await update.answer("📄 Tugma nomini kiriting", reply_markup=KeyboardManger.back())
    
    elif update.text == "❌ Yo'q":
        await state.set_state(AdsMenu.confirm_send)
        await state.update_data(replay_markup = None)
        data = await state.get_data()
        m = await bot.copy_message(chat_id=update.from_user.id,
                                from_chat_id=db.DATA_CHANEL_ID,
                                message_id=data['message_id'])

        await bot.send_message(
            chat_id=update.from_user.id,
            reply_to_message_id = m.message_id,
            text ="👆 Xabar shunaqa ko'rnishda bo'ladi. Xabarni yuborish uchun yuborish tugmasni bosing", reply_markup=KeyboardManger.send_message())
    
    else:
        await update.answer("❗️ Xabarga tugma qo'shishni xohlaysizmi?", reply_markup=KeyboardManger.yes_or_no())


brodcaster = Semaphore()

@r.message(AdsMenu.confirm_send)
async def confirm_send(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.set_state(AdsMenu.wana_add_button)
        await state.update_data(replay_markup = None)
        await update.answer("🔘 Xabarga tugma qoshamizmi?", reply_markup=KeyboardManger.yes_or_no())

    elif update.text == "🚀 Yuborish":
        await send_ads(update, state)
        
    else:
        await update.answer("❗️ Xabarni yuborishni xohlaysizmi?", reply_markup=KeyboardManger.send_message())

async def send_ads(update: types.Message, state: FSMContext):
    data = await state.get_data() 
    await state.set_state(AdminPanel.main)
    await update.answer("⏳")
    await update.answer("Xabarni yuborish boshlandi ...", reply_markup=KeyboardManger.panel(await db.get_courses()))
    
   
    course_id = data.get('course_id')
    course = await db.get_course(id=course_id) if course_id else None
    all = data.get('all')
    replay_markup = None
    message_id = data.get('message_id')

    if data.get('replay_markup'):
        replay_markup = InlineKeyboardManager.ads_button(data.get('button_name'), data.get('url'))

    sended = 0
    blocked = 0
    async with brodcaster:
        for user in await db.get_users():
            if not user.is_active:
                continue

            if all:
                status = await send(user, message_id, replay_markup)
                if status:
                    sended+=1
                else:
                    blocked+=1
                await sleep(0.05)

            elif course:
                sub = await db.get_subscribtion(course=course.id, user_id=user.id)
                if sub:
                    status = await send(user, message_id, replay_markup)
                    if status:
                        sended+=1
                    else:
                        blocked+=1
                    await sleep(0.05)
     
    await update.answer(f"Xabar yuborish yakunladi \n🚀 Yuborildi: {sended} \n❌ Tark etganlar: {blocked}")

from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramRetryAfter,
)
from data import UserStatus
from asyncio import sleep
    
async def send(user: User, message_id: int, replay_markup : types.InlineKeyboardMarkup | None) -> int:
    try:
        await bot.copy_message(chat_id=user.id,
                               from_chat_id=db.DATA_CHANEL_ID,
                               message_id=message_id,
                               reply_markup=replay_markup)
        
        return True

    except TelegramForbiddenError:
        await db.update_user(user.id, status=UserStatus.left)
        return False
        
    except TelegramRetryAfter as e:
        await sleep(e.retry_after+2)
        await bot.copy_message(chat_id=user.id,
                               from_chat_id=db.DATA_CHANEL_ID,
                               message_id=message_id,
                               reply_markup=replay_markup)
        
        return True

    except Exception as e:
        print('sender:', e)
        return False


@r.message(AdsMenu.get_button_name)
async def get_button_name(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.set_state(AdsMenu.wana_add_button)
        await state.update_data(replay_markup = None)
        await update.answer("🔘 Xabarga tugma qoshamizmi?", reply_markup=KeyboardManger.yes_or_no())
    

    elif update.text and len(update.text) > 40:
        await update.answer("❗️ Tugma nomi 40 ta belgidan ko'p bo'lmasligi kerak", reply_markup=KeyboardManger.back())

    elif update.text:
        await state.set_state(AdsMenu.get_button_url)
        await state.update_data(button_name = update.text)
        await update.answer("🔗 Tugma uchun havola kirting", reply_markup=KeyboardManger.back())

import re
url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"


@r.message(AdsMenu.get_button_url)
async def get_button_url(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.set_state(AdsMenu.get_button_name)
        await update.answer("Tugma nomini kiriting", reply_markup=KeyboardManger.back())

    elif update.text and re.match(url_pattern, update.text):
        await state.set_state(AdsMenu.confirm_send)
        await state.update_data(replay_markup = True, url = update.text)
        data = await state.get_data()
        name = data['button_name']
        m = await bot.copy_message(chat_id=update.from_user.id,
                                from_chat_id=db.DATA_CHANEL_ID,
                                message_id=data['message_id'],
                                reply_markup=InlineKeyboardManager.ads_button(name, update.text))
        await bot.send_message(
            chat_id=update.from_user.id,
            reply_to_message_id = m.message_id,
            text ="👆 Xabar shunaqa ko'rnishda bo'ladi. Xabarni yuborish uchun yuborish tugmasni bosing", reply_markup=KeyboardManger.send_message())

    else:
        await update.answer("Iltimos faqat havola yuboring", reply_markup=KeyboardManger.back())
