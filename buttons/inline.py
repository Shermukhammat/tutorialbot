from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data import Course, CourseButton, CourseButtonType, Test, Subscription
import math


class AutoButtons:
    def __init__(self, max_width: int = 5, max_height: int = 50):
        self.rows: list[list[InlineKeyboardButton]] = []
        self.max_width = max_width
        self.max_height = max_height

    def add(self, button: InlineKeyboardButton, new_line: bool = False) -> bool:
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
    def reply_markup(self) -> InlineKeyboardMarkup:
        if self.rows:
            return InlineKeyboardMarkup(inline_keyboard=self.rows, resize_keyboard=True)


class InlineKeyboardManager:
    def edit_course(course: Course) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Pullik" if course.pro else "❌ Pullik", callback_data='pro')],
            [InlineKeyboardButton(text="✏️ Nomi", callback_data='edit_name'), InlineKeyboardButton(text="✏️ Malumoti", callback_data='edit_media')],
            [InlineKeyboardButton(text="✅ Qator tashla" if course.new_line else "❌ Qator tashla", callback_data='new_line')],
            [InlineKeyboardButton(text="🗑 O'chirish", callback_data='delete')]
        ])
    

    def edit_course_button(button: CourseButton, pro : bool = False) -> InlineKeyboardMarkup:
        inline_keyboard=[
                [InlineKeyboardButton(text="✅ Qator tashla" if button.new_line else "❌ Qator tashla", callback_data='new_line')],
                [InlineKeyboardButton(text="✏️ Nomi", callback_data='edit_name')],
                [InlineKeyboardButton(text="🗑 O'chirish", callback_data='delete')]
            ]
        if pro:
            inline_keyboard[1].append(InlineKeyboardButton(text="🔓 Ochiq" if button.open else "🔒 Yopiq", callback_data='open'))   
        
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    

    def tests_paginator(tests: list[Test],
                        page: int = 0,
                        per_page: int = 10) -> InlineKeyboardMarkup:
        """Return an inline keyboard that paginates test list.

        • page      – zero-based page index
        • per_page  – buttons per page
        """
        bt = AutoButtons(max_width=5)
        offset = page * per_page
        new_line = False

        for test in tests[offset:offset+per_page]:
            bt.add(InlineKeyboardButton(text = str(tests.index(test)+1), callback_data=f"test_{test.id}"))

        if page:
            bt.add(InlineKeyboardButton(text = "⬅️", callback_data=f"page_{page-1}"), new_line=True)
            new_line = True
        if offset + per_page < len(tests):
            bt.add(InlineKeyboardButton(text = "➡️", callback_data=f"page_{page+1}"), new_line=not new_line)
        
        return bt.reply_markup
    

    def test_edit_button(test: Test, next: int = None, prev: int = None) -> InlineKeyboardMarkup:
        bt=AutoButtons()
        new_line = False

        bt.add(InlineKeyboardButton(text="🔄 Qaytadan kirtish", callback_data=f"edit_{test.id}"))
        bt.add(InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"delete_{test.id}"), new_line=True)

        if prev:
            bt.add(InlineKeyboardButton(text="⬅️", callback_data=f"test_{prev}"), new_line=True)
            new_line = True
        if next:
            bt.add(InlineKeyboardButton(text="➡️", callback_data=f"test_{next}"), new_line=not new_line)
        
        return bt.reply_markup
    

    def course_users_paginator(subscribtions: list[Subscription], offset: int = 0, limit: int = 10, leng: int = 20) -> InlineKeyboardMarkup:
        bt=AutoButtons()
        new_line = False

        for index, sub in enumerate(subscribtions):
            bt.add(InlineKeyboardButton(text=f"{index+1}", callback_data=f"sub_{sub.id}"))
        
        if offset:
            bt.add(InlineKeyboardButton(text="⬅️", callback_data=f"subnext_{offset-limit}"), new_line=True)
            new_line = True
        if offset + limit < leng:
            bt.add(InlineKeyboardButton(text="➡️", callback_data=f"subnext_{offset+limit}"), new_line=not new_line)
        return bt.reply_markup


    def delete_user_sub(id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗑 O'chrish", callback_data=f"delete_sub_{id}")]
            ])
    
    def buy_course(admin_username: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👮🏻‍♂️ Adminga yozish", url = f'https://t.me/{admin_username}')]
            ])