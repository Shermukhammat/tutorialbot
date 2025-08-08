from aiogram import Router, Dispatcher, types, F
from loader import db, dp, bot
from data import CourseButtonType
from buttons import KeyboardManger, InlineKeyboardManager
from aiogram.fsm.context import FSMContext
from asyncio import sleep, Semaphore
from states.user import UserStates
from utils import TestManager
from aiogram.types import ContentType



r = Router()
dp.include_router(r)
sema = Semaphore()


@r.message(UserStates.get_phone_number, F.content_type.in_(
        {ContentType.CONTACT,}
    ))
async def get_phone_number(update: types.Message, state: FSMContext):
    await db.update_user(update.from_user.id, phone_number=update.contact.phone_number)

    await state.set_state(UserStates.course_menu)
    data = await state.get_data()
    course = await db.get_course(id = data['course_id'])
    buttons = await db.get_course_buttons(course.id)
    sub = await db.get_subscribtion(user_id=update.from_user.id, course=course.id)
    if course.pro:
        await update.answer(f"{course.name} kursi", reply_markup=KeyboardManger.course_menu(buttons, pro = course.pro, subscribed = bool(sub)))
    else:
        await update.answer(f"{course.name} kursi", reply_markup=KeyboardManger.course_menu(buttons, pro = course.pro))


@r.message(UserStates.get_phone_number)
async def get_phone_number_text(update: types.Message):
    await update.reply("Iltimos telefon raqamni yuborish tugmasni bosing. Zarur paytda aynan shu raqam orqali siz bilan bog'lanamiz.", reply_markup=KeyboardManger.request_phone_number())


@r.message(UserStates.update_phone_number, F.content_type.in_(
        {ContentType.CONTACT, ContentType.TEXT}
    ))
async def update_contact(update: types.Message, state: FSMContext):
    if update.text == '⬅️ Orqaga':
        await state.clear()
        subs = [sub.course for sub in await db.get_subscribtions(update.from_user.id)]
        await update.answer("🏠 Bosh menyu", reply_markup=KeyboardManger.home(await db.get_courses(), subs = subs))
    
    elif update.contact:
        await db.update_user(update.from_user.id, phone_number=update.contact.phone_number)
        await state.clear()
        subs = [sub.course for sub in await db.get_subscribtions(update.from_user.id)]
        await update.answer("✅ Telefon raqam muvaffaqiyatli o'zgartirildi", reply_markup=KeyboardManger.home(await db.get_courses(), subs = subs))
    
    else:
        await bot.send_message(chat_id=update.from_user.id, 
                               text="Iltimos telefon raqamni yuborish tugmasni bosing yoki orqaga tugmasni bosing",
                               reply_markup=KeyboardManger.request_phone_number(back = True))

