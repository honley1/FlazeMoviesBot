from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from motor.core import AgnosticDatabase as MongoDB

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="👤 Профиль")],
    [KeyboardButton(text="🎬 Искать фильм/сериал")]
], resize_keyboard=True)


async def get_channels_ikb(db: MongoDB) -> InlineKeyboardMarkup:
    inline_kb = InlineKeyboardBuilder()

    channels_name = await db.channels.distinct("name")
    channels_link = await db.channels.distinct("link")

    for channel_link, channel_name in zip(channels_link, channels_name):

        inline_kb.row(InlineKeyboardButton(text=channel_name, url=channel_link))

    inline_kb.row(InlineKeyboardButton(text="Проверить подписку ✅🎬", callback_data="check_subscribe"))

    return inline_kb.as_markup()


