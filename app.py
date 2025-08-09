from loader import dp, db, bot 
import asyncio, logging, middlewares, handlers
from utils.mytime import get_next_day_sec


async def dayly_loop():
    while True:
        await asyncio.sleep(get_next_day_sec())
        await db.reset_dayly_tracks()

async def main():
    await db.init()
    db.bot = await bot.get_me()
    print(f'[bot]: @{db.bot.username}')

    asyncio.create_task(dayly_loop())
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())