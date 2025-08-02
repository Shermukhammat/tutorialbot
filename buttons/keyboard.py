from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from data import Course, CourseButton, CourseButtonType
import random

class AutoButtons:
    def __init__(self, max_width: int = 5, max_height: int = 50):
        self.rows: list[list[KeyboardButton]] = []
        self.max_width = max_width
        self.max_height = max_height

    def add(self, button: KeyboardButton, new_line: bool = False) -> bool:
        # Start a new row if asked or if there is no row yet
        if new_line or not self.rows:
            if len(self.rows) >= self.max_height:
                return False                    # keyboard is full
            self.rows.append([])

        row = self.rows[-1]

        # If current row is full, open a new one
        if len(row) >= self.max_width:
            if len(self.rows) >= self.max_height:
                return False
            self.rows.append([])
            row = self.rows[-1]

        row.append(button)
        return True

    @property
    def reply_markup(self) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(keyboard=self.rows, resize_keyboard=True)





class KeyboardManger:
    def home(courses: list[Course]) -> ReplyKeyboardMarkup:
        buttons = AutoButtons()
        for course in courses:
            buttons.add(KeyboardButton(text=course.name), new_line = course.new_line)

        buttons.add(KeyboardButton(text = "📖 Yordam"), new_line=True)
        buttons.add(KeyboardButton(text = "💎 Sotib olish"))
        return buttons.reply_markup
    
    def panel(courses: list[Course]) -> ReplyKeyboardMarkup:
        buttons = AutoButtons()
        for course in courses:
            buttons.add(KeyboardButton(text=course.name), new_line = course.new_line)

        buttons.add(KeyboardButton(text = "➕ Kurs qo'shish"), new_line = True)
        buttons.add(KeyboardButton(text = "📢 Xabar jo'natish"), new_line = True)
        buttons.add(KeyboardButton(text = "⚙️ Sozlamalar"))
        
        buttons.add(KeyboardButton(text = "⬅️ Chiqish"), new_line = True)
        return buttons.reply_markup   
    
    def back() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text = "⬅️ Orqaga")]
        ], resize_keyboard=True)
    

    def course_admin_menu(course_buttons: list[CourseButton]) -> ReplyKeyboardMarkup:
        buttons = AutoButtons()
        for course_button in course_buttons:
            buttons.add(KeyboardButton(text=course_button.name), new_line = course_button.new_line)

        buttons.add(KeyboardButton(text = "➕ Test"), new_line = True)
        buttons.add(KeyboardButton(text = "➕ Media"))
        buttons.add(KeyboardButton(text = "➕ Menu"))
        buttons.add(KeyboardButton(text = "⬅️ Orqaga"), new_line = True)
        return buttons.reply_markup
    

    def yes1():
        buttons = [KeyboardButton(text="Xa"), 
                   KeyboardButton(text="Yo'q"), 
                   KeyboardButton(text="Bilmadim"), 
                   KeyboardButton(text ="Albatta yo'q")]
        random.shuffle(buttons)
        keyboard = [[b] for b in buttons]
        keyboard.append([KeyboardButton(text="⬅️ Orqaga")])
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

    def yes2():
        buttons = [KeyboardButton(text="Xa 100%"), 
                   KeyboardButton(text="Yo'g'e"), 
                   KeyboardButton(text="Aniqmas"),
                   KeyboardButton(text="Xa lekin 100% emas"),
                   KeyboardButton(text="Albatta yo'q")]
        random.shuffle(buttons)
        keyboard = [[b] for b in buttons]
        keyboard.append([KeyboardButton(text="⬅️ Orqaga")])
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True) 
    
