from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from data import Course


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
    
    