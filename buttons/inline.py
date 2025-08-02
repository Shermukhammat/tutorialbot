from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data import Course



class InlineKeyboardManager:
    def edit_course(course: Course) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Pullik" if course.pro else "❌ Pullik", callback_data='pro')],
            [InlineKeyboardButton(text="✏️ Nomi", callback_data='edit_name'), InlineKeyboardButton(text="✏️ Malumoti", callback_data='edit_media')],
            [InlineKeyboardButton(text="✅ Qator tashla" if course.new_line else "❌ Qator tashla", callback_data='new_line')],
            [InlineKeyboardButton(text="🗑 O'chirish", callback_data='delete')]
        ])