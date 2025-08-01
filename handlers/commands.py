from loader import dp, db, bot
from aiogram import types 
from data import User, UserStatus
from aiogram.filters import Command, CommandStart
from buttons import KeyboardManger



@dp.message(CommandStart())
async def start_command(update: types.Message, user: User):
    reply_markup = KeyboardManger.home(await db.get_courses())
    
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
async def admin_command(update: types.Message, user: User):
    if user.is_admin:
        KeyboardManger.home
        await update.answer("🎛 Admin panel",
                            reply_markup = KeyboardManger.panel(await db.get_courses()))
    
    elif user.id == db.DEV_ID:
        await db.update_user(user.id, is_admin = True)
        await update.answer("Dasturchi siz endi adminsiz")

        await bot.set_my_commands([
            types.BotCommand(command = 'help', description = '📖 Yordam'),
            types.BotCommand(command = 'buy', description = '💎 Kurs sotib olish'),
            types.BotCommand(command = 'admin', description = '👮🏻‍♂️ Admin panel'),
            types.BotCommand(command = 'stats', description = '📊 Bot statistikasi')
            ], types.BotCommandScopeChat(chat_id = update.chat.id))

@dp.message(Command('commands'))
async def admin_command(update: types.Message, user: User):
    if user.id == db.DEV_ID: 
        await bot.set_my_commands([
            types.BotCommand(command = 'help', description = '📖 Yordam'),
            types.BotCommand(command = 'buy', description = '💎 Kurs sotib olish')
            ])

@dp.message()
async def main_handler(update: types.Message, user: User):
    await update.answer("Bosh menu", reply_markup=KeyboardManger.home(await db.get_courses()))