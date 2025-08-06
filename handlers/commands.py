from loader import dp, db, bot
from aiogram import types 
from data import User, UserStatus
from aiogram.filters import Command, CommandStart, CommandObject
from buttons import KeyboardManger
from aiogram.fsm.context import FSMContext
from states import AdminPanel
from asyncio import Semaphore, sleep


sema = Semaphore()

@dp.message(Command(commands=['start', 'restart']))
async def start_command(update: types.Message, command: CommandObject, state: FSMContext):
    if await state.get_state():
        await state.clear()
    user = await db.get_user(update.from_user.id)
    subs = [sub.course for sub in await db.get_subscribtions(update.from_user.id)]
    reply_markup=KeyboardManger.home(await db.get_courses(), subs = subs)


    if command.args:
        async with sema:
            sub = await db.get_subscribtion(token = command.args)
            send_info = False
            if sub:
                course = await db.get_course(id = sub.course)
                sub2 = await db.get_subscribtion(user_id = update.from_user.id, course=sub.course)
                if sub2:
                    await update.answer_sticker('CAACAgIAAxkBAAIQYWiSIXUXyWo9h1A24SHuwZ8J27nNAAL4AANWnb0KcRzji0O3QeA2BA')
                    await update.answer(f"❗️ Sizda allaqachon {course.name} kursi uchun aktiv obuna bor", reply_markup=reply_markup)
                
                else:
                    await db.update_subscribtion(sub.id, user_id = update.from_user.id, token=None)
                    send_info = True

        if send_info:
            await update.delete()
            st = await update.answer_sticker("CAACAgIAAxkBAAIHa2iPFGMVV-5m13haRm5nXlLXO51_AAJJAgACVp29CiqXDJ0IUyEONgQ")
            await sleep(3)
            await st.delete()
            await update.answer("🎉")
            await update.answer(f"{update.from_user.first_name} siz {course.name} kursiga obuna bo'ldingiz", reply_markup=reply_markup)

        return
    
    if user.is_admin:
        await update.answer(f"👮🏻‍♂️ Admin {update.from_user.full_name} \n🗓 Ro'yxatdan o'tdi: {user.registred_readble}",
                            reply_markup = reply_markup)

    elif user.status == UserStatus.left:
        await db.update_user(user.id, status = UserStatus.active)
        await update.answer(f"Assalomu alaykum {update.from_user.full_name}. Sizni qayta ko'rganimdan xursandman!",
                            reply_markup = reply_markup)
    
    else:
        await update.answer(f"👤 Foydalanuvchi: {update.from_user.full_name} \n🗓 Ro'yxatdan o'tdi: {user.registred_readble}",
                            reply_markup = reply_markup)



@dp.message(Command('dev'))
async def dev_command(update: types.Message):
    if update.from_user.id == db.DEV_ID:
        await update.answer("🧑‍💻 Dasturchi sozlamalari \n\n/admin dasturchini admin qilish \n/exit botdan chiqish \n/commands Komandalarni yanglash")


@dp.message(Command('exit'))
async def exit_command(update: types.Message):
    if update.from_user.id == db.DEV_ID:
        await db.remove_user(update.from_user.id)
        await update.answer("Botdan chiqdingiz", reply_markup=types.ReplyKeyboardRemove())
        
        await bot.set_my_commands([
            types.BotCommand(command = 'help', description = '📖 Yordam'),
            types.BotCommand(command = 'buy', description = '💎 Kurs sotib olish')
            ], types.BotCommandScopeChat(chat_id = update.chat.id))

@dp.message(Command('admin'))
async def admin_command(update: types.Message, state: FSMContext):
    user = await db.get_user(update.from_user.id)
    if user.is_admin:
        await state.set_state(state = AdminPanel.main)
        await update.answer("🎛 Admin panel",
                            reply_markup = KeyboardManger.panel(await db.get_courses()))
    
    elif user.id == db.DEV_ID:
        await db.update_user(user.id, is_admin = True)
        await update.answer("Dasturchi siz endi adminsiz")

        await bot.set_my_commands([
            types.BotCommand(command = 'admin', description = '👮🏻‍♂️ Admin panel'),
            types.BotCommand(command = 'stats', description = '📊 Bot statistikasi'),
            types.BotCommand(command = 'restart', description = '🔄 Botni qayta ishga tushrish'),
            types.BotCommand(command = 'number', description = '📱 Telefon raqamni yangilash'),
            types.BotCommand(command = 'help', description = '📖 Yordam')
            ], types.BotCommandScopeChat(chat_id = update.chat.id))

@dp.message(Command('commands'))
async def admin_command(update: types.Message):
    user = await db.get_user(update.from_user.id)
    if user.id == db.DEV_ID:
        await bot.set_my_commands([
            types.BotCommand(command = 'restart', description = '🔄 Botni qayta ishga tushrish'),
            types.BotCommand(command = 'number', description = '📱 Telefon raqamni yangilash'),
            types.BotCommand(command = 'help', description = '📖 Yordam')
            ], scope=types.BotCommandScopeAllPrivateChats())
        await update.answer("Bot komandalari yangilandi")

    for user in await db.get_users():
        if user.is_admin:
            await bot.set_my_commands([
            types.BotCommand(command = 'admin', description = '👮🏻‍♂️ Admin panel'),
            types.BotCommand(command = 'stats', description = '📊 Bot statistikasi'),
            types.BotCommand(command = 'restart', description = '🔄 Botni qayta ishga tushrish'),
            types.BotCommand(command = 'number', description = '📱 Telefon raqamni yangilash'),
            types.BotCommand(command = 'help', description = '📖 Yordam')
            ], types.BotCommandScopeChat(chat_id = user.id))

# @dp.message()
# async def main_handler(update: types.Message, user: User):
#     await update.answer("Bosh menu", reply_markup=KeyboardManger.home(await db.get_courses()))