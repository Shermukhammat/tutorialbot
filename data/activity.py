from aiocache import SimpleMemoryCache
from asyncpg.pool import PoolAcquireContext, Pool



class ActivityTracker:
    def __init__(self) -> None: 
        self.activity_cache = SimpleMemoryCache(ttl = 200)
        self.pool : Pool = None

    async def reset_dayly_tracks(self):
        async with self.pool.acquire() as conn:
            conn : Pool
            await conn.execute(""" DELETE FROM activity; """)

    
    async def get_dayly_activity(self) -> int:
        async with self.pool.acquire() as conn:
            conn : Pool
            row = await conn.fetchrow(""" SELECT count(*) FROM activity; """)
            if row:
                return row[0]