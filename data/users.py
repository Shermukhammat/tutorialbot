from asyncpg.pool import PoolAcquireContext, Pool
from datetime import datetime
from aiocache import SimpleMemoryCache
from datetime import datetime
from pytz import timezone
import asyncpg, asyncio

tz = timezone('Asia/Tashkent')

class UserStatus:
    active = 1
    left = 2


class User:
    def __init__(self,
                 id : int = None, 
                 fullname : str = None,
                 lang : str = 'uz',
                 registered : datetime = None,
                 status : int = UserStatus.active,
                 is_admin: bool = False
                 ) -> None:
        self.id = id
        self.lang = lang
        self.fullname = fullname
        self.status = status
        self.is_admin = is_admin
        
        if registered:
            self.registered = registered
        else:
            self.registered = datetime.now(tz)

    @property
    def registred_readble(self) -> str:
        return f"{self.registered.year}.{self.registered.month}.{self.registered.day} {self.registered.hour}:{self.registered.minute}"

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.active
    
    def __str__(self) -> str:
        return f"User(id={self.id}, fullname={self.fullname}, lang={self.lang}, registered={self.registered}, status={self.status}, is_admin={self.is_admin})"




class UsersDB:
    def __init__(self) -> None: 
        self.users_cache  = SimpleMemoryCache(ttl = 60)
        self.pool : Pool = None

    async def init_user_manger(self):
        async with self.pool.acquire() as conn:
            conn : Pool
            await conn.execute("""CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                fullname TEXT NOT NULL,
                registered TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                status INTEGER NOT NULL DEFAULT 1,
                is_admin BOOLEAN NOT NULL DEFAULT FALSE,
                lang TEXT NOT NULL DEFAULT 'uz'
            );""")
            await conn.execute("""CREATE TABLE IF NOT EXISTS activity (
                id BIGINT PRIMARY KEY
            );""")
    
    async def is_user(self, id : int) -> bool:
        if await self.users_cache.get(id):
            return True
        
        user = await get_user_from_db(self.pool, id)
        if user:
            await self.users_cache.set(id, user)
            return True

    async def register_user(self, user : User):
        await registr_user_to_db(self.pool, user)
        await self.users_cache.set(user.id, user)
        
    
    async def get_user(self, id : int) -> User:
        user = await self.users_cache.get(id)
        if user:
            return user
        
        user = await get_user_from_db(self.pool, id)
        if user:
            await self.users_cache.set(user.id, user)
            return user
        
    
    async def remove_user(self, id : int):
        await self.users_cache.delete(id)
        await delete_user_from_db(self.pool, id)

    async def update_user(self, id : int, **kwargs):
        await update_user_data_from_db(self.pool, id, **kwargs)
        user = await get_user_from_db(self.pool, id)
        if user:
            await self.users_cache.set(id, user)

    async def get_useres(self) -> list[User]:
        async with self.pool.acquire() as conn:
            conn : Pool
            users = []
            rows = await conn.fetch("""SELECT * FROM users;""")
            for row in rows:
                users.append(User(id = row['id'], 
                                   registered = row['registered'], 
                                   status = row['status'], 
                                   fullname = row['fullname'], 
                                   lang = row['lang'], 
                                   is_admin=row['is_admin'])
                             )
        return users

async def update_user_data_from_db(pool : Pool, id : int, **kwargs):
    async with pool.acquire() as conn:
        conn : Pool
        for key, value in kwargs.items():
            await conn.execute(f""" UPDATE users SET {key} = $1 WHERE id = $2""", value, id)

async def delete_user_from_db(pool : Pool, id : int):
    async with pool.acquire() as conn:
        conn : Pool
        await conn.execute(""" DELETE FROM users WHERE id = $1""", id)


async def registr_user_to_db(pool : Pool, user : User):
    async with pool.acquire() as conn:
        conn : Pool
        query = """ INSERT INTO users (id, registered, status, fullname, lang, is_admin) VALUES($1, $2, $3, $4, $5, $6); """
        values = (user.id, user.registered, user.status, user.fullname, user.lang, user.is_admin)
        await conn.execute(query, *values)


async def get_user_from_db(pool : Pool, id : int) -> User:
    async with pool.acquire() as conn:
        conn : Pool
        row = await conn.fetchrow("""SELECT * FROM users WHERE id = $1""", id)
        if row:
            await conn.execute(""" INSERT INTO activity (id) VALUES ($1) ON CONFLICT (id) DO NOTHING; """, id)
            return User(id = id, 
                    registered=row['registered'],
                    status=row['status'],
                    fullname=row['fullname'],
                    lang=row['lang'],
                    is_admin=row['is_admin'])
        




async def __test__():
    db = UsersDB()
    db.pool = await asyncpg.create_pool(user='postgres', password='your_password', database='tutorial', host='localhost')
    await db.init_user_manger()


    user = User(id=1, fullname="John Doe", lang="en")
    # await db.register_user(user)
    await db.remove_user(1)
    print(await db.get_user(1))


if __name__ == "__main__":
    asyncio.run(__test__())
    