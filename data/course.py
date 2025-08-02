from asyncpg import Pool, create_pool, Connection
from aiocache import SimpleMemoryCache
from abc import ABC
import asyncio


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


class CourseButtonType:
    TEST = 'test'
    MEDIA = 'media'
    INNER_MENU = 'inner_menu'



class CourseButton:
    def __init__(self, id: int = None, name: str = None, course: int = None, type: str = None, new_line: bool = False):
        self.id = id
        self.name = name
        self.course = course
        self.type = type
        self.new_line = new_line

    def __str__(self):
        return f"CourseButton(id={self.id}, name={self.name}, course={self.course}, type={self.type})"



class CoursesManager(ABC):
    def __init__(self):
        self.pool: Pool = None
        self.__courses_cache = SimpleMemoryCache(ttl=20)

    async def init_courses(self):
        async with self.pool.acquire() as conn:
            conn : Connection
            # await conn.execute("DROP TABLE IF EXISTS course_buttons CASCADE;")

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
                               type TEXT
                               );""")
            await conn.execute(""" CREATE TABLE IF NOT EXISTS tests (
                               id SERIAL PRIMARY KEY,
                               courses_button INTEGER REFERENCES course_buttons(id) ON DELETE CASCADE, 
                               question TEXT,
                               media INTEGER,
                               options TEXT[]
                               ); """)
            await conn.execute(""" CREATE TABLE IF NOT EXISTS lessons (
                               id SERIAL PRIMARY KEY,
                               courses_button INTEGER REFERENCES course_buttons(id) ON DELETE CASCADE,
                               media INTEGER[]
                               );""")
            

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
            await conn.execute(""" INSERT INTO course_buttons (name, course, type, new_line) VALUES ($1, $2, $3, $4);""", 
                               button.name, button.course, button.type, button.new_line)
            
        await self.__courses_cache.delete(f"cb{button.course}")

    async def get_course_button(self, id : int) -> CourseButton:
        async with self.pool.acquire() as conn:
            conn : Connection
            row = await conn.fetchrow(""" SELECT * FROM course_buttons WHERE id = $1;""", id)
        if row:
            return CourseButton(id=row['id'], name=row['name'], course=row['course'], type=row['type'], new_line=row['new_line'])
    
    async def get_course_buttons(self, course_id : int, use_cache: bool = True) -> list[CourseButton]:
        buttons = await self.__courses_cache.get(f'cb{course_id}')
        if buttons and use_cache:
            return buttons
        
        async with self.pool.acquire() as conn:
            conn: Connection
            rows = await conn.fetch(""" SELECT * FROM course_buttons WHERE course = $1;""", course_id)
            buttons = [CourseButton(id=row['id'], name=row['name'], course=row['course'], type=row['type'], new_line=row['new_line']) for row in rows]
            await self.__courses_cache.set(f'cb{course_id}', buttons)
        return buttons
    
    async def delete_course_button(self, id : int):
        async with self.pool.acquire() as conn:
            conn : Connection
            await conn.execute(""" DELETE FROM course_buttons WHERE id = $1;""", id)

        await self.__courses_cache.delete(f"cb{id}")
        await self.__courses_cache.delete("courses")

    async def update_course_button(self, id : int = None, **kwargs):
        async with self.pool.acquire() as conn:
            conn : Connection
            for key, value in kwargs.items():
                await conn.execute(f""" UPDATE course_buttons SET {key} = $1 WHERE id = $2""", value, id)

        
        await self.__courses_cache.delete(f"cb{id}")
        await self.__courses_cache.delete("courses")
                

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