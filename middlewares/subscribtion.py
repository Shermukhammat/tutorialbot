from aiogram import BaseMiddleware, Router, F, Dispatcher
from aiogram.types import Message, User as TGUser, TelegramObject, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from typing import Dict, Any, Awaitable, Callable
from loader import db, dp, bot
from buttons import KeyboardManger
from data import User, DataBase
from aiogram.dispatcher.event.bases import SkipHandler 
from asyncio import Semaphore
from aiocache import SimpleMemoryCache
# from aiogram.exceptions import ChatAdminRequired, ChatNotFound, Unauthorized

sema = Semaphore()
cache = SimpleMemoryCache(ttl = 60)

class SubscribetionMiddleware(BaseMiddleware):
    def __init__(self, db: DataBase):
        self.db = db

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        if self.db.CHANELS:
            tg_user: TGUser = data["event_from_user"]
            if not await cache.get(tg_user.id):
                await check_subscribtion(self.db, tg_user, event)
        
        return await handler(event, data)



async def is_subscribed(user_id : int, chanel : str):
    try:
        member  = await bot.get_chat_member(chat_id = chanel, user_id = user_id)
        if member and member.status != 'left':
            return True
        return False  
    except Exception as e:
        # print(e)
        return False

async def check_subscribtion(db: DataBase, tg_user: TGUser, event: Message | CallbackQuery) -> User:
    chanels = []
    # print(tg_user.id)
    for chanel in db.CHANELS:
        if not await is_subscribed(tg_user.id, chanel.id):
            chanels.append(chanel)
    
    if chanels:
        replay_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=chanel.name, url=chanel.url)] for chanel in chanels
        ])
        replay_markup.inline_keyboard.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check")])

        if isinstance(event, Message):
            await event.answer("Botdan foydalnishu uchun quydagi kanalga obuna bo'ling 👇",
                               reply_markup=replay_markup)
        else:
            if event.data == "check":
                await event.answer("❗️ Kanalga obuna bo'lmagansiz", show_alert=True)
            else:
                await bot.send_message(text = "Botdan foydalnishu uchun quydagi kanalga obuna bo'ling 👇",
                                       chat_id=tg_user.id,
                                        reply_markup=replay_markup)
        
        raise SkipHandler()
    
    await cache.set(tg_user.id, True)



dp.message.middleware(SubscribetionMiddleware(db))
dp.callback_query.middleware(SubscribetionMiddleware(db))