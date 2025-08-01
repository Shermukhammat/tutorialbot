from loader import dp, db, bot 
import asyncio, logging, middlewares, handlers



async def main():
    await db.init()
    db.bot = await bot.get_me()
    print(f'[bot]: @{db.bot.username}')

    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())