from asyncpg import Pool, create_pool, Connection
from aiocache import SimpleMemoryCache
from abc import ABC
import asyncio
from datetime import datetime, timedelta
from pytz import timezone
from datetime import timezone as dt_tz

tz = timezone('Asia/Tashkent')

class Course:
    def __init__(self, id: int = None, 
                 name: str = None, 
                 new_line: bool = False,
                 pro: bool = True,
                 message: int = None):
        self.id = id
        self.name = name
        self.new_line = new_line
        self.pro = pro
        self.message = message

    def __str__(self):
        return f"Course(id={self.id}, name={self.name}, new_line={self.new_line}, pro={self.pro}, message={self.message})"


class Subscription:
    def __init__(self, id: int = None, 
                 user_id: int = None, 
                 token: str = None, 
                 course: int = None, 
                 created_at: datetime = None,
                 full_name: str = None,
                 phone_number: str = None):
        self.id = id
        self.user_id = user_id
        self.token = token
        self.course = course
        self.created_at = created_at if created_at else datetime.now(tz)
        self.full_name = full_name if full_name else 'Kutilmoqda'
        self.phone_number = phone_number if phone_number else ''

    @property
    def created_at_readble(self) -> str:
        dt = self.created_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=dt_tz.utc)  # safety for naive
        dt = dt.astimezone(tz)
        return dt.strftime("%Y.%m.%d %H:%M")


    def __str__(self):
        return f"Subscription(id={self.id}, user={self.user_id}, token={self.token})"


class CourseButtonType:
    TEST = 'test'
    MEDIA = 'media'
    INNER_MENU = 'inner_menu'



class CourseButton:
    def __init__(self, id: int = None, 
                 name: str = None, 
                 course: int = None, 
                 type: str = None, 
                 new_line: bool = False, 
                 open: bool = False,
                 mix_tests: bool = False,
                 mix_options: bool = False,
                 media: list[int] = [],
                 time: int = None):
        self.id = id
        self.name = name
        self.course = course
        self.type = type
        self.new_line = new_line
        self.open = open
        self.mix_tests = mix_tests
        self.mix_options = mix_options
        self.time = time
        self.media = media

    def __str__(self):
        return f"CourseButton(id={self.id}, name={self.name}, course={self.course}, type={self.type})"

    @property
    def display_time(self) -> str:
        return str(self.time) if self.time else '♾️'

class Test:
    def __init__(self, id: int = None, courses_button: int = None, question: str = None, media: int = None, options: list[str] = None, info: str = None):
        self.id = id
        self.courses_button = courses_button
        self.question = question
        self.media = media
        self.options = options
        self.info = info
    
    @property
    def safe_question(self) -> str:
        limit = 255 - 15
        if len(self.question) > limit:
            return self.question[:limit] + '...'
        return self.question


class CoursesManager(ABC):
    def __init__(self):
        self.pool: Pool = None
        self.__courses_cache = SimpleMemoryCache(ttl=20)

    async def init_courses(self):
        async with self.pool.acquire() as conn:
            conn : Connection
            # await conn.execute("DROP TABLE IF EXISTS subscritpion CASCADE;")

            await conn.execute(""" CREATE TABLE IF NOT EXISTS courses (
                               id SERIAL PRIMARY KEY, 
                               name TEXT UNIQUE,
                               new_line BOOLEAN NOT NULL DEFAULT FALSE,
                               pro BOOLEAN,
                               message INTEGER
                               );  """)
            await conn.execute(""" CREATE TABLE IF NOT EXISTS course_buttons (
                               id SERIAL PRIMARY KEY, 
                               name TEXT,
                               course INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                               new_line BOOLEAN NOT NULL DEFAULT FALSE,
                               type TEXT,
                               open BOOLEAN NOT NULL DEFAULT FALSE,
                               mix_tests BOOLEAN NOT NULL DEFAULT FALSE,
                               mix_options BOOLEAN NOT NULL DEFAULT FALSE,
                               time INTEGER
                               );""")
            await conn.execute("ALTER TABLE course_buttons ADD COLUMN IF NOT EXISTS media INTEGER[] NOT NULL DEFAULT '{}';")
            # await conn.execute("ALTER TABLE course_buttons ADD COLUMN IF NOT EXISTS mix_options BOOLEAN NOT NULL DEFAULT FALSE;")
            # await conn.execute("ALTER TABLE course_buttons ADD COLUMN IF NOT EXISTS time INTEGER;")
            await conn.execute(""" CREATE TABLE IF NOT EXISTS tests (
                               id SERIAL PRIMARY KEY,
                               courses_button INTEGER REFERENCES course_buttons(id) ON DELETE CASCADE, 
                               question TEXT,
                               media INTEGER,
                               options TEXT[],
                               info TEXT
                               ); """)
            await conn.execute(""" CREATE TABLE IF NOT EXISTS lessons (
                               id SERIAL PRIMARY KEY,
                               courses_button INTEGER REFERENCES course_buttons(id) ON DELETE CASCADE,
                               media INTEGER[]
                               );""")
            await conn.execute(""" CREATE TABLE IF NOT EXISTS subscribtions (
                               id SERIAL PRIMARY KEY,
                               user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
                               course INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                               token TEXT
                               );
                               """)
            await conn.execute(""" ALTER TABLE subscribtions ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();""")
            

    async def get_course(self, id : int = None, name : str = None) -> Course:
        if name is None and id is None:
            raise ValueError("name or id must be provided")

        async with self.pool.acquire() as conn:
            conn : Connection 
            if id:
                row = await conn.fetchrow(""" SELECT * FROM courses WHERE id = $1;""", id)  
            else:
                row = await conn.fetchrow(""" SELECT * FROM courses WHERE name = $1;""", name)
            
        if row:
            return Course(id=row['id'], name=row['name'], new_line=row['new_line'], pro=row['pro'], message=row['message'])

            
    async def delete_course(self, id : int = None, name : str = None):
        async with self.pool.acquire() as conn:
            conn : Connection
            if id:
                await conn.execute(""" DELETE FROM courses WHERE id = $1;""", id)
            elif name:
                await conn.execute(""" DELETE FROM courses WHERE name = $1;""", name)
            else:
                raise ValueError("id or name must be provided")
        
        await self.__courses_cache.delete(f"cb{id}")
        await self.__courses_cache.delete("courses")

    async def update_course(self, id : int, **kwargs):
        async with self.pool.acquire() as conn:
            conn : Connection
            for key, value in kwargs.items():
                await conn.execute(f""" UPDATE courses SET {key} = $1 WHERE id = $2""", value, id)

        await self.__courses_cache.delete('courses')
        await self.__courses_cache.delete(f"cb{id}")

    async def add_course(self, course : Course) -> int:
        async with self.pool.acquire() as conn:
            conn : Connection
            await conn.execute(""" INSERT INTO courses (name, new_line, pro, message) VALUES ($1, $2, $3, $4);""", 
                               course.name, course.new_line, course.pro, course.message)
        
        await self.__courses_cache.delete("courses")

        course = await self.get_course(name=course.name)
        if course:
            return course.id

    async def get_courses(self, use_cache : bool = True) -> list[Course]:
        courses = await self.__courses_cache.get('courses')
        if courses and use_cache:
            return courses
        async with self.pool.acquire() as conn:
            conn : Connection
            rows = await conn.fetch(""" SELECT * FROM courses ORDER BY id DESC;""")
        
        courses = [Course(id=row['id'], name=row['name'], new_line=row['new_line'], pro=row['pro'], message=row['message']) for row in rows]
        await self.__courses_cache.set('courses', courses)
        return courses


    async def add_course_button(self, button : CourseButton):
        async with self.pool.acquire() as conn:
            conn : Connection
            await conn.execute(""" INSERT INTO course_buttons (name, course, type, new_line, open, media, mix_tests, mix_options, time) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);""", 
                               button.name, button.course, button.type, button.new_line, button.open, button.media, button.mix_tests, button.mix_options, button.time)
            
        await self.__courses_cache.delete(f"cb{button.course}")

    async def get_course_button(self, course_id : int = None, name: str = None, id : int = None) -> CourseButton:
        async with self.pool.acquire() as conn:
            conn : Connection
            if name:
                row = await conn.fetchrow(""" SELECT * FROM course_buttons WHERE course = $1 AND name = $2;""", course_id, name)
            elif id:
                row = await conn.fetchrow(""" SELECT * FROM course_buttons WHERE id = $1;""", id)
            else:
                raise ValueError("name and course_id or id  must be provided")

        if row:
            return CourseButton(id=row['id'], 
                                name=row['name'], 
                                course=row['course'], 
                                type=row['type'], 
                                new_line=row['new_line'], 
                                open=row['open'],
                                mix_tests=row['mix_tests'],
                                media=row['media'],
                                mix_options=row['mix_options'],
                                time=row['time'])
    
    async def get_course_buttons(self, course_id : int, use_cache: bool = True) -> list[CourseButton]:
        buttons = await self.__courses_cache.get(f'cb{course_id}')
        if buttons and use_cache:
            return buttons
        
        async with self.pool.acquire() as conn:
            conn: Connection
            rows = await conn.fetch(""" SELECT * FROM course_buttons WHERE course = $1 ORDER BY id;""", course_id)
            buttons = [CourseButton(id=row['id'], name=row['name'], course=row['course'], type=row['type'], new_line=row['new_line'], open=row['open'], mix_tests=row['mix_tests'], mix_options=row['mix_options'], time=row['time'], media=row['media']) for row in rows]
            await self.__courses_cache.set(f'cb{course_id}', buttons)
        return buttons
    
    async def delete_course_button(self, id : int):
        bt = await self.get_course_button(id = id) 
        async with self.pool.acquire() as conn:
            conn : Connection
            await conn.execute(""" DELETE FROM course_buttons WHERE id = $1;""", id)

        if bt:   
            await self.__courses_cache.delete(f"cb{bt.course}")
        await self.__courses_cache.delete("courses")

    async def update_course_button(self, id : int = None, **kwargs):
        async with self.pool.acquire() as conn:
            conn : Connection
            for key, value in kwargs.items():
                await conn.execute(f""" UPDATE course_buttons SET {key} = $1 WHERE id = $2""", value, id)

        bt = await self.get_course_button(id = id) 
        if bt:   
            await self.__courses_cache.delete(f"cb{bt.course}")
        await self.__courses_cache.delete("courses")
                

    async def get_test(self, id : int) -> Test:
        async with self.pool.acquire() as conn:
            conn : Connection
            row = await conn.fetchrow(""" SELECT * FROM tests WHERE id = $1;""", id)
        
        if row:
            return Test(id=row['id'], courses_button=row['courses_button'], question=row['question'], media=row['media'], options=row['options'], info=row['info'])

    async def add_test(self, test : Test):
        async with self.pool.acquire() as conn:
            conn : Connection
            await conn.execute(""" INSERT INTO tests (courses_button, question, media, options, info) VALUES ($1, $2, $3, $4, $5);""", 
                               test.courses_button, test.question, test.media, test.options, test.info)
        
    async def get_tests(self, course_button_id : int = None) -> list[Test]:
        async with self.pool.acquire() as conn:
            conn : Connection
            rows = await conn.fetch(""" SELECT * FROM tests WHERE courses_button = $1;""", course_button_id)
        
        return [Test(id=row['id'], courses_button=row['courses_button'], question=row['question'], media=row['media'], options=row['options'], info=row['info']) for row in rows]

    async def delete_test(self, id: int):
        async with self.pool.acquire() as conn:
            conn : Connection
            await conn.execute(""" DELETE FROM tests WHERE id = $1;""", id)

    async def update_test(self, id: int, **kwargs):
        async with self.pool.acquire() as conn:
            conn : Connection
            for key, value in kwargs.items():
                await conn.execute(f""" UPDATE tests SET {key} = $1 WHERE id = $2""", value, id)


    async def get_subscribtion(self, id : int = None, token: str = None, user_id: int = None, course: int = None) -> Subscription:
        async with self.pool.acquire() as conn:
            conn : Connection
            if id:
                row = await conn.fetchrow(""" SELECT * FROM subscribtions WHERE id = $1;""", id)
            elif token:
                row = await conn.fetchrow(""" SELECT * FROM subscribtions WHERE token = $1;""", token)
            elif user_id and course:
                row = await conn.fetchrow(""" SELECT * FROM subscribtions WHERE user_id = $1 AND course = $2;""", user_id, course)
            else:
                raise ValueError("id or token or user_id and course must be provided")

        if row:
            return Subscription(id=row['id'], user_id=row['user_id'], token=row['token'], course=row['course'], created_at=row['created_at'])
    
    async def get_subscribtions(self, user_id: int) -> list[Subscription]:
        async with self.pool.acquire() as conn:
            conn : Connection
            rows = await conn.fetch(""" SELECT * FROM subscribtions WHERE user_id = $1;""", user_id)
        return [Subscription(id=row['id'], user_id=row['user_id'], token=row['token'], course=row['course'], created_at=row['created_at']) for row in rows]

    async def add_subscribtion(self, subscribtion : Subscription):
        async with self.pool.acquire() as conn:
            conn : Connection
            await conn.execute(""" INSERT INTO subscribtions (user_id, token, course) VALUES ($1, $2, $3);""", subscribtion.user_id, subscribtion.token, subscribtion.course)

    async def delete_subscribtion(self, id : int):
        async with self.pool.acquire() as conn:
            conn : Connection
            await conn.execute(""" DELETE FROM subscribtions WHERE id = $1;""", id)
    
    async def clear_course_subs(self, course_id: int):
        async with self.pool.acquire() as conn:
            conn : Connection
            await conn.execute(""" DELETE FROM subscribtions WHERE course = $1;""", course_id)


    async def update_subscribtion(self, id: int, **kwargs):
        async with self.pool.acquire() as conn:
            conn : Connection
            for key, value in kwargs.items():
                await conn.execute(f""" UPDATE subscribtions SET {key} = $1 WHERE id = $2""", value, id)

    async def course_sub_count(self, course_id : int) -> int:
        async with self.pool.acquire() as conn:
            conn : Connection
            row = await conn.fetchrow("""SELECT count(subscribtions.id) FROM subscribtions 
                                    FULL JOIN users ON subscribtions.user_id = users.id
                                    WHERE course = $1""", course_id)
            
        if row:
            return row['count']
        return 0

    async def get_course_subs(self, course_id : int, offset: int = 0, limit: int = 10) -> list[Subscription]:
        async with self.pool.acquire() as conn:
            conn : Connection
            rows = await conn.fetch("""SELECT s.*, u.fullname, u.phone_number
FROM subscribtions AS s
LEFT JOIN users AS u ON u.id = s.user_id
WHERE s.course = $1
ORDER BY s.created_at DESC
OFFSET $2 LIMIT $3;""", course_id, offset, limit)
        
        return [Subscription(id=row['id'], user_id=row['user_id'], token=row['token'], course=row['course'], created_at=row['created_at'], full_name=row['fullname'], phone_number=row['phone_number']) for row in rows]
    
    
async def main():
    class Tetser(CoursesManager):
        def __init__(self):
            pass 
        

    db = Tetser()
    db.pool = await create_pool(user='postgres', password='your_password', database='tutorial', host='localhost')
    await db.init_courses()

    course = Course(name='Matematika')
    # await db.add_course(course)
    # await db.delete_course(id = 1)
    print(await db.get_course(name='Matematika'))
    

if __name__ == '__main__':
    asyncio.run(main())