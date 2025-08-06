from aiogram.fsm.state import StatesGroup, State


class AdminPanel(StatesGroup):
    main = State()
    add_course = State()
    course_menu = State()
    add_test_block = State()

    edit_course_name = State()
    edit_course_media = State()
    delete_course = State()


class AdminCourseMneu(StatesGroup):
    main = State()

    edit_name = State()
    edit_media = State()
    delete1 = State()
    delete2 = State()

    clear_subs_1 = State()
    clear_subs_2 = State()


class AdminCourseButton(StatesGroup):
    main = State()

    add = State()
    add_media_button = State()
    add_menu_button = State()
    edit_name = State()

    delete1 = State()
    delete2 = State()


class AdminTestBlock(StatesGroup):
    main = State()
    get_test = State()
    edit_test = State()

    edit_name = State()
    edit_time = State()
    delete = State()