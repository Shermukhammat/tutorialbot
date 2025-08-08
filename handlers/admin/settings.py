from aiogram import Router, Dispatcher, types, F
from states import AdminPanel, AdminCourseMneu, AdminCourseButton, AdminTestBlock, AdminMedia, Settings
from loader import db, dp, bot
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import Semaphore
from data import Course, CourseButtonType, Subscription
from utils.mytime import can_edit
from .main import r, back_to_course_menu
from aiogram.types import ContentType
from uuid import uuid4
from aiogram.enums import ParseMode
from ..commands import set_user_commands, set_admin_commands


sema = Semaphore()

@r.callback_query(Settings.main, F.data == 'update_help')
async def update_help_content(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(Settings.update_help_content)
    await update.message.answer("⬆️ Yangi yordam kontentini kirting", reply_markup=KeyboardManger.back())


@r.callback_query(Settings.main, F.data == 'add_admin')
async def add_admin(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(Settings.add_admin)
    await update.message.answer("↩️ Admin qilmoqchi bo'lgan foydalanuvchi idsini menga yuboring. Id ni /id komandasi oraqli olish mumkun", 
                                reply_markup=KeyboardManger.back())
    

@r.message(Settings.add_admin)
async def get_admin_wrapper(update: types.Message, state: FSMContext):
    async with sema:
        await get_admin(update, state)


async def get_admin(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.set_state(Settings.main)
        await update.answer("Sozlamalar menyusi", reply_markup=KeyboardManger.settings())

    if len(await db.get_admins()) >= 15:
        await update.reply("❗️ Adminlar soni 15tadan ko'p bo'lishi mumkun emas")

    elif update.text and update.text.isnumeric():
        if update.from_user.id == int(update.text):
            await update.answer("O'zingzni idngzni yubormang")
            return
        
        user = await db.get_user(int(update.text))
        if user:
            await state.set_state(Settings.main)
            await db.update_user(user.id, is_admin=True)
            await update.reply("✅ Admin qo'shildi", reply_markup=KeyboardManger.settings())

            await set_admin_commands(user.id)
            await bot.send_message(chat_id=user.id,
                                   text="🎉")
            subs = [sub.course for sub in await db.get_subscribtions(user.id)]
            reply_markup=KeyboardManger.home(await db.get_courses(), subs = subs)
            await bot.send_message(chat_id=user.id,
                                   text=f"Tabriklaymiz {user.fullname} sizga adminlik huquqi berildi", 
                                   reply_markup=reply_markup)
        else:
            await update.reply("❗️ Bunday foydlanuvchi botdan ro'yxatdan o'tmagan", reply_markup=KeyboardManger.back())

    else:
        await update.answer("Iltimos yangi admin idsini son kornishda kirting", reply_markup=KeyboardManger.back())


@r.callback_query(Settings.main, F.data == 'remove_admin')
async def delete_admin(update: types.CallbackQuery, state: FSMContext):
    await state.set_state(Settings.delete_admin)
    await update.message.answer("🔫 Olib tashlamoqchi bo'lgan admin ID raqamini kiriting (faqat raqamlar qabul qilinadi)", 
                                reply_markup=KeyboardManger.back())
    

@r.message(Settings.delete_admin)
async def delete_admin_handler(update: types.Message, state: FSMContext):
    if update.text == "⬅️ Orqaga":
        await state.set_state(Settings.main)
        await update.answer("Sozlamalar menyusi", reply_markup=KeyboardManger.settings())

    elif update.text.isnumeric():
        id = int(update.text)
        user = await db.get_user(id)
        if user and user.is_admin:
            await db.update_user(user.id, is_admin=False)
            await state.set_state(Settings.main)
            await update.answer("✅ Admin o'chirildi", reply_markup=KeyboardManger.settings())

            await set_user_commands(user.id)
            await bot.send_message(chat_id=user.id,
                                   text="😞")
            subs = [sub.course for sub in await db.get_subscribtions(user.id)]
            reply_markup=KeyboardManger.home(await db.get_courses(), subs = subs)
            await bot.send_message(chat_id=user.id,
                                   text=f"{user.fullname} sizdan adminlik huqulari {update.from_user.full_name} tomonidan olib tashlandi", 
                                   reply_markup=reply_markup)
            
            ctx : FSMContext = dp.fsm.get_context(bot, user.id, user.id)
            if ctx and await ctx.get_state():
                await ctx.clear()
        else:
            await update.answer("❗️ Bunda admin topilmadi", reply_markup=KeyboardManger.back())
    else:
        await update.answer("❗️ Iltimos faqat raqam ko'rinishda kiriting", reply_markup=KeyboardManger.back())


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
        
    elif update.text == '👮🏻‍♂️ Adminlar':
        admins = await db.get_admins()
        text = 'Adminlar: '
        for index, admin in enumerate(admins):
            text += f"\n\n{index+1}. {admin.fullname} {'@'+admin.username if admin.username else ''} \n🆔: `{admin.id}`"

        try:
            await update.answer(text, reply_markup=InlineKeyboardManager.admins_button(),
                            parse_mode=ParseMode.MARKDOWN)
        except:
            await update.answer(text, reply_markup=InlineKeyboardManager.admins_button())

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
    
        