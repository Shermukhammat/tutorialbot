from aiogram.fsm.state import StatesGroup, State


class AdminPanel(StatesGroup):
    main = State()
    add_course = State()
    course_menu = State()
    add_course_button = State()

    edit_course_name = State()
    edit_course_media = State()
    delete_course = State()


class AdminCourseMneu(StatesGroup):
    main = State()

    edit_name = State()
    edit_media = State()
    delete1 = State()
    delete2 = State()