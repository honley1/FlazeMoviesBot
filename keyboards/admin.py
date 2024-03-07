from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from motor.core import AgnosticDatabase as MongoDB

admin_main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👤 Профиль")],
    [KeyboardButton(text="🎬 Искать фильм/сериал")],
    [KeyboardButton(text="👑 Админка")]
], resize_keyboard=True)

admin_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📺 Добавить канал")],
    [KeyboardButton(text="🚮 Список пользователей")],
    [KeyboardButton(text="👨‍💻 Добавить фильм/сериал")],
    [KeyboardButton(text="⬅️ Назад")]
], resize_keyboard=True)

cancel_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🚫 Отменить")]
], resize_keyboard=True)
