import os
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from motor.core import AgnosticDatabase as MongoDB
from pymongo.errors import DuplicateKeyError

from keyboards.admin import admin_main_keyboard
from keyboards.client import main_keyboard, get_channels_ikb
from states.client import GetMovies

load_dotenv()

router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID"))


async def check_subscribe(channels_id, user_id, message: Message):
    for channel_id in channels_id:
        is_user_not_subscribe = await message.bot.get_chat_member(chat_id=channel_id, user_id=user_id)

        if is_user_not_subscribe.status == "left":
            return False

    return True


@router.message(CommandStart())
async def start_cmd(message: Message, db: MongoDB) -> None:
    if message.chat.type == "private":

        channels_id = await db.channels.distinct("_id")
        channels_name = await db.channels.distinct("name")

        if await check_subscribe(channels_id, message.from_user.id, message):
            user_id = message.from_user.id
            username = message.from_user.username
            fullname = message.from_user.full_name
            current_date = datetime.utcnow().date().strftime("%Y-%m-%d")

            text = f"""
            👋 Добро пожаловать <b>{fullname}</b> !\n\n\n🎬 Выберите действие 
            """

            try:
                await db.users.insert_one({
                    "_id": user_id,
                    "username": username,
                    "fullname": fullname,
                    "channels": channels_name,
                    "date": current_date
                })

                await message.answer(text,
                                     reply_markup=main_keyboard if message.from_user.id != ADMIN_ID
                                     else admin_main_keyboard,
                                     parse_mode="html")
            except DuplicateKeyError:
                await message.answer(text,
                                     reply_markup=main_keyboard if message.from_user.id != ADMIN_ID
                                     else admin_main_keyboard,
                                     parse_mode="html")
        else:
            await message.answer("<b>Прежде чем начать пользоваться ботом, "
                                 "вы должны подписаться на все каналы ниже 👇🎬</b>",
                                 reply_markup=await get_channels_ikb(db),
                                 parse_mode='html')


@router.message(F.text == "👤 Профиль")
async def profile_cmd(message: Message, db: MongoDB):
    if message.chat.type == "private":

        channels_id = await db.channels.distinct("_id")

        if await check_subscribe(channels_id, message.from_user.id, message):
            user = await db.users.find_one({"_id": message.from_user.id})

            user_id = message.from_user.id
            username = message.from_user.username
            full_name = message.from_user.full_name
            channels = ", ".join(user['channels']) if user['channels'] else 0
            registration_date = user['date']

            text = (f"ID: <b>{user_id}</b>\n\n"
                    f"🌎 Username: <b>{username}</b>\n"
                    f"👤 Полное имя: <b>{full_name}</b>\n"
                    f"🎬 Каналы: <b>{channels}</b>\n"
                    f"⌛️ Дата регистрации: <b>{registration_date}</b>")

            await message.answer(text,
                                 reply_markup=main_keyboard if message.from_user.id != ADMIN_ID
                                 else admin_main_keyboard,
                                 parse_mode="html")
        else:
            await message.answer("<b>Прежде чем начать пользоваться ботом, "
                                 "вы должны подписаться на все каналы ниже 👇🎬</b>",
                                 reply_markup=await get_channels_ikb(db),
                                 parse_mode='html')


@router.callback_query(F.data == "check_subscribe")
async def check_subscribe_cmd(query: CallbackQuery, db: MongoDB):
    if query.message.chat.type == "private":

        channels_id = await db.channels.distinct("_id")
        channels_name = await db.channels.distinct("name")

        if await check_subscribe(channels_id, query.from_user.id, query.message):
            user_id = query.from_user.id
            username = query.from_user.username
            fullname = query.from_user.full_name
            current_date = datetime.utcnow().date().strftime("%Y-%m-%d")

            text = f"""
                   👋 Добро пожаловать <b>{fullname}</b> !\n\n\n🎬 Выберите действие 
                   """

            try:
                await db.users.insert_one({
                    "_id": user_id,
                    "username": username,
                    "fullname": fullname,
                    "channels": channels_name,
                    "date": current_date
                })

                await query.message.answer(text,
                                           reply_markup=main_keyboard if query.from_user.id != ADMIN_ID
                                           else admin_main_keyboard,
                                           parse_mode="html")

                await query.answer()

            except DuplicateKeyError:
                await query.message.answer(text,
                                           reply_markup=main_keyboard if query.from_user.id != ADMIN_ID
                                           else admin_main_keyboard,
                                           parse_mode="html")

                await query.answer()

        else:
            await query.message.answer("<b>Прежде чем начать пользоваться ботом, "
                                       "вы должны подписаться на все каналы ниже 👇🎬</b>",
                                       reply_markup=await get_channels_ikb(db),
                                       parse_mode='html')
            await query.answer()


@router.message(F.text == "⬅️ Назад")
async def back_cmd(message: Message, db: MongoDB):
    if message.chat.type == "private":

        channels_id = await db.channels.distinct("_id")

        if await check_subscribe(channels_id, message.from_user.id, message):
            fullname = message.from_user.full_name

            await message.answer(f"👋 Добро пожаловать <b>{fullname}</b> !\n\n\n🎬 Выберите действие ",
                                 parse_mode='html',
                                 reply_markup=main_keyboard if message.from_user.id != ADMIN_ID
                                 else admin_main_keyboard)
        else:
            await message.answer("<b>Прежде чем начать пользоваться ботом, "
                                 "вы должны подписаться на все каналы ниже 👇🎬</b>",
                                 reply_markup=await get_channels_ikb(db),
                                 parse_mode='html')


@router.message(F.text == "🎬 Искать фильм/сериал")
async def back_cmd(message: Message, db: MongoDB, state: FSMContext):
    if message.chat.type == "private":

        channels_id = await db.channels.distinct("_id")

        if await check_subscribe(channels_id, message.from_user.id, message):

            await message.answer("Введите <b>код</b> от фильма/сериала", parse_mode='html')

            await state.set_state(GetMovies.movies_id)

        else:
            await message.answer("<b>Прежде чем начать пользоваться ботом, "
                                 "вы должны подписаться на все каналы ниже 👇🎬</b>",
                                 reply_markup=await get_channels_ikb(db),
                                 parse_mode='html')


@router.message(GetMovies.movies_id)
async def back_cmd(message: Message, db: MongoDB, state: FSMContext):
    if message.chat.type == "private":

        channels_id = await db.channels.distinct("_id")

        if await check_subscribe(channels_id, message.from_user.id, message):

            movies_id = message.text

            movies = await db.movies.find_one({"_id": movies_id})

            if movies:
                await message.bot.send_photo(
                    chat_id=message.from_user.id,
                    photo=movies['icon']['file_id'],
                    caption=f"ID: <b>{movies['_id']}</b>\nНазвание: <b>{movies['name']}</b>\n\n"
                            f"Описание: <b>{movies['description']}</b>",
                    parse_mode='html'
                )

                await state.clear()
            else:
                await message.answer("🎬 Фильм/сериал не найден")

        else:
            await message.answer("<b>Прежде чем начать пользоваться ботом, "
                                 "вы должны подписаться на все каналы ниже 👇🎬</b>",
                                 reply_markup=await get_channels_ikb(db),
                                 parse_mode='html')

