from aiocache import SimpleMemoryCache
from asyncpg.pool import PoolAcquireContext, Pool



class Info:
    dayly_users : int = 0
    activ_users : int = 0
    lived_users : int = 0
    courses_count : int = 0

    today_joined : int = 0
    week_joined : int = 0
    month_joined : int = 0


class Statistic:
    def __init__(self) -> None: 
        self.stat_cache = SimpleMemoryCache(ttl = 20)
        self.pool : Pool = None

    async def get_statistic(self) -> Info:            
        info = await self.stat_cache.get('info')
        if info:
            return info
        
        info = await get_info_from_db(self.pool)
        await self.stat_cache.set('info', info)
        return info

    
async def get_info_from_db(pool : Pool) -> Info:
    async with pool.acquire() as conn:
        conn : Pool
        info = Info()

        row = await conn.fetchrow("SELECT count(*) FROM users WHERE status = 1;")
        if row:
            info.activ_users = row[0]

        row = await conn.fetchrow("SELECT count(*) FROM users WHERE status = 2;")
        if row:
            info.lived_users = row[0]

        row = await conn.fetchrow("SELECT count(*) FROM courses;")
        if row:
            info.courses_count = row[0]

        row = await conn.fetchrow("SELECT count(*) FROM activity;")
        if row:
            info.dayly_users = row[0]

        row = await conn.fetchrow("SELECT count(*) FROM users WHERE registered::date = CURRENT_DATE AND status = 1;")
        if row:
            info.today_joined = row[0]

        row = await conn.fetchrow("SELECT count(*) FROM users WHERE registered >= DATE_TRUNC('week', CURRENT_DATE) AND status = 1;")
        if row:
            info.week_joined = row[0]

        row = await conn.fetchrow("SELECT count(*) FROM users WHERE registered >= DATE_TRUNC('month', CURRENT_DATE) AND status = 1;")
        if row:
            info.month_joined = row[0]
        

        return info