from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonPollType
from data import Course, CourseButton, CourseButtonType, Subscription
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
    def home(courses: list[Course], subs : list[int] = []) -> ReplyKeyboardMarkup:
        buttons = AutoButtons()
        for course in courses:
            if course.id in subs:
                buttons.add(KeyboardButton(text=course.name), new_line = course.new_line)
            elif course.pro:
                buttons.add(KeyboardButton(text=f"👑 {course.name}"), new_line = course.new_line)
            else:
                buttons.add(KeyboardButton(text=course.name), new_line = course.new_line)

        buttons.add(KeyboardButton(text = "📖 Yordam"), new_line=True)
        # buttons.add(KeyboardButton(text = "💎 Sotib olish"))
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
    
    def test_buttons(skip_button: bool| None = False) -> ReplyKeyboardMarkup:
        if skip_button:
            return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text = "➡️ Keyingi")],
            [KeyboardButton(text = "❌ Bekor qilish")]
        ], resize_keyboard=True)

        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text = "❌ Bekor qilish")]
        ], resize_keyboard=True)
    
    def media_saver(save: bool = False) -> ReplyKeyboardMarkup:
        if save:
            return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text = "✅ Saqlash")],
            [KeyboardButton(text = "⬅️ Orqaga")]
        ], resize_keyboard=True)
        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text = "⬅️ Orqaga")]], resize_keyboard=True)
    
    def time_button() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text = "♾️ Vaxt belgilanmasin")],
            [KeyboardButton(text = "⬅️ Orqaga")]
        ], resize_keyboard=True)
    
    def make_quiz() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Test tuzish", request_poll=KeyboardButtonPollType(type='quiz'))],
            [KeyboardButton(text = "⬅️ Orqaga")]
        ], resize_keyboard=True)

    def course_admin_menu(course_buttons: list[CourseButton], pro: bool = True) -> ReplyKeyboardMarkup:
        buttons = AutoButtons()
        for course_button in course_buttons:
            buttons.add(KeyboardButton(text=course_button.name), new_line = course_button.new_line)

        buttons.add(KeyboardButton(text = "➕ Test blok"), new_line = True)
        buttons.add(KeyboardButton(text = "➕ Media"))
        if pro:
            buttons.add(KeyboardButton(text = "➕ Foydalnuvchi"))

            buttons.add(KeyboardButton(text="🎓 Foydalnuvchilar"), new_line=True)
            buttons.add(KeyboardButton(text = "🧹 Foydalnuvchilarni tozlash"))
        
        buttons.add(KeyboardButton(text = "⬅️ Orqaga"), new_line = True)
        return buttons.reply_markup
    

    def yes_or_no() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="✅ Xa"), KeyboardButton(text="❌ Yo'q")],
            [KeyboardButton(text = "⬅️ Orqaga")]
        ], resize_keyboard=True)
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
    
    def edit_course_button(button: CourseButton, pro : bool = False) -> ReplyKeyboardMarkup:
        if button.type == CourseButtonType.TEST:
            keyboard=[
                [KeyboardButton(text="➕ Test qo'shish"), KeyboardButton(text="📋 Testlar")],
                [KeyboardButton(text="✅ Qator tashla" if button.new_line else "❌ Qator tashla"), KeyboardButton(text="✏️ Nomi")],
                [KeyboardButton(text=f"⏳ Vaxt: {button.display_time}"), KeyboardButton(text= "✅ Testlarni arlashtir" if button.mix_tests else "❌ Testlarni arlashtir")],
                [KeyboardButton(text="✅ Varyantlarni arlashtir" if button.mix_options else "❌ Varyantlarni arlashtir")],
                [KeyboardButton(text="🗑 O'chirish")],
                [KeyboardButton(text="⬅️ Orqaga")]
            ]
            keyboard[-2] += [KeyboardButton(text="🔓 Ochiq" if button.open else "🔒 Yopiq")] if pro else []
            return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        
        elif button.type == CourseButtonType.MEDIA:
            keyboard=[
                [KeyboardButton(text="🔄 Mediani yangilash"), KeyboardButton(text="📁 Media")],
                [KeyboardButton(text="✅ Qator tashla" if button.new_line else "❌ Qator tashla"), KeyboardButton(text="✏️ Nomi")],
                [KeyboardButton(text="🗑 O'chirish")],
                [KeyboardButton(text="⬅️ Orqaga")]
            ]
            keyboard[-2] += [KeyboardButton(text="🔓 Ochiq" if button.open else "🔒 Yopiq")] if pro else []
            return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        

    def course_menu(buttons: list[CourseButton], pro : bool = False, subscribed: bool = False) -> ReplyKeyboardMarkup:
        bt = AutoButtons()
        # print('subscribed:', subscribed, 'pro:', pro)
        for button in buttons:
            if pro and not subscribed:
                bt.add(KeyboardButton(text=f"{'' if button.open else '🔒 '}{button.name}"), new_line=button.new_line)
            else:
                bt.add(KeyboardButton(text=f"{button.name}"), new_line=button.new_line)

        bt.add(KeyboardButton(text="⬅️ Orqaga"), new_line=True)
        return bt.reply_markup
    

    def request_phone_number(back : bool = False) -> ReplyKeyboardMarkup:
        if back:
            return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact = True)],
            [KeyboardButton(text="⬅️ Orqaga")]
            ], resize_keyboard=True)
        
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact = True)]
        ], resize_keyboard=True)