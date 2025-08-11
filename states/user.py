from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    course_menu = State()
    in_test = State()
    get_phone_number = State()
    update_phone_number = State()


class InnerMenu(StatesGroup):
    main = State()
    in_test = State()