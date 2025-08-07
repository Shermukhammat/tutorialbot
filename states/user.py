from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    course_menu = State()
    in_test = State()