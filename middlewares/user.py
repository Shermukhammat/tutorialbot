from aiogram import BaseMiddleware, Router, F, Dispatcher
from aiogram.types import Message, User as TGUser, TelegramObject, CallbackQuery
from typing import Dict, Any, Awaitable, Callable
from loader import db, dp
from buttons import KeyboardManger
from data import User, DataBase
from aiogram.dispatcher.event.bases import SkipHandler 
from asyncio import Semaphore


sema = Semaphore()

class UserMiddleware(BaseMiddleware):
    def __init__(self, db: DataBase):
        self.db = db

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        tg_user: TGUser = data["event_from_user"]
        user = await self.db.get_user(tg_user.id)
        if user is None:
            user = await register_user(self.db, tg_user, event)
            
        return await handler(event, data)


async def register_user(db: DataBase, tg_user: TGUser, event: Message | CallbackQuery) -> User:
    async with sema:
        user = await db.get_user(tg_user.id)
        if user:
            return user
        
        user = User(id = tg_user.id, fullname = tg_user.full_name, username=tg_user.username)
        await db.register_user(user)
        if isinstance(event, Message):
            await event.answer(f"Assalomu alaykum {user.fullname} xush kelibsiz! Men {db.bot.full_name} man",
                               reply_markup = KeyboardManger.home(await db.get_courses()))
        else:
            await event.message.answer(f"Assalomu alaykum {user.fullname} xush kelibsiz! Men {db.bot.full_name} man",
                               reply_markup = KeyboardManger.home(await db.get_courses()))
    raise SkipHandler()



dp.message.middleware(UserMiddleware(db))
dp.callback_query.middleware(UserMiddleware(db))