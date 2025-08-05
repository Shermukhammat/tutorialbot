import asyncpg, asyncio
from asyncpg import Pool, Connection
from .params import ParamsManager
from aiogram.types import User as AiogramUser
from .users import User, UserStatus, UsersDB
from .activity import ActivityTracker
from .course import CoursesManager, Course, CourseButton, CourseButtonType, Test, Subscription
# from .statistic import Statistic
# from .subscribtion import SubscribtionDB




class DataBase(ParamsManager, UsersDB, ActivityTracker, CoursesManager):
    def __init__(self, config_file_path : str) -> None:
        ParamsManager.__init__(self, config_file_path)
        UsersDB.__init__(self)
        ActivityTracker.__init__(self)
        CoursesManager.__init__(self)
        # Statistic.__init__(self)
        # SubscribtionDB.__init__(self)
        self.pool : Pool = None
        self.bot : AiogramUser = None

    async def init(self):
        self.pool : Pool = await asyncpg.create_pool(user=self.config.user, 
                                         password=self.config.pasword,
                                         database=self.config.database, 
                                         host=self.config.host,
                                         port = self.config.port)

        await self.init_user_manger()
        await self.init_courses()
    

    async def close(self):
        await self.pool.close()

   


if __name__ == '__main__':
    pass
    # asyncio.run(db.creat_tables())