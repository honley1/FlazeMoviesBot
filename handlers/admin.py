import json
import os

from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from motor.core import AgnosticDatabase as MongoDB
from pymongo.errors import DuplicateKeyError

from handlers.client import check_subscribe, start_cmd
from keyboards.admin import admin_menu_keyboard, admin_main_keyboard, cancel_keyboard
from keyboards.client import main_keyboard, get_channels_ikb
from states.admin import AddChannel, AddMovies

load_dotenv()

router = Router()

ADMIN_ID = int(os.getenv("ADMIN_ID"))


@router.message(F.text == "👑 Админка")
async def admin_cmd(message: Message, db: MongoDB):
    if message.chat.type == "private":

        channels_id = await db.channels.distinct("_id")

        if await check_subscribe(channels_id, message.from_user.id, message):
            if message.from_user.id == ADMIN_ID:
                await message.answer("Выберите действие 🙇🏿‍♂️👑",
                                     parse_mode='html',
                                     reply_markup=admin_menu_keyboard)
            else:
                await message.answer("Вы не админ 🚫",
                                     parse_mode='html')
        else:
            await message.answer("<b>Прежде чем начать пользоваться ботом, "
                                 "вы должны подписаться на все каналы ниже 👇🎬</b>",
                                 reply_markup=await get_channels_ikb(db),
                                 parse_mode='html')


@router.message(F.text == "🚮 Список пользователей")
async def get_users_cmd(message: Message, db: MongoDB):
    if message.chat.type == "private":

        channels_id = await db.channels.distinct("_id")

        if await check_subscribe(channels_id, message.from_user.id, message):
            if message.from_user.id == ADMIN_ID:

                users = await db.users.find({}).to_list(None)

                user_data = []

                for user in users:
                    user_info = {
                        "ID": user['_id'],
                        "Username": user['username'],
                        "Fullname": user['fullname'],
                        "Channels": user['channels'],
                        "Date": user['date']
                    }

                    user_data.append(user_info)

                total_users = len(user_data)
                user_data.append({'Количество пользователей': total_users})

                with open("user_data.json", "w", encoding="utf-8") as insert_data:
                    json.dump(user_data, insert_data, indent=4, ensure_ascii=False)

                await message.answer_document(document=FSInputFile("user_data.json"),
                                              reply_markup=main_keyboard if message.from_user.id != ADMIN_ID
                                              else admin_main_keyboard)

            else:
                await message.answer("Вы не админ 🚫",
                                     parse_mode='html')
        else:
            await message.answer("<b>Прежде чем начать пользоваться ботом, "
                                 "вы должны подписаться на все каналы ниже 👇🎬</b>",
                                 reply_markup=await get_channels_ikb(db),
                                 parse_mode='html')


@router.message(F.text == "🚫 Отменить")
async def cancel_cmd(message: Message, state: FSMContext, db: MongoDB):
    await state.clear()

    await start_cmd(message, db)


@router.message(F.text == "📺 Добавить канал")
async def add_channel_cmd(message: Message, db: MongoDB, state: FSMContext):
    if message.chat.type == "private":

        channels_id = await db.channels.distinct("_id")

        if await check_subscribe(channels_id, message.from_user.id, message):
            if message.from_user.id == ADMIN_ID:
                await message.answer("🆔 Введите <b>id</b> канала: ",
                                     parse_mode='html',
                                     reply_markup=cancel_keyboard)
                await state.set_state(AddChannel.channel_id)
            else:
                await message.answer("Вы не админ 🚫",
                                     parse_mode='html')
        else:
            await message.answer("<b>Прежде чем начать пользоваться ботом, "
                                 "вы должны подписаться на все каналы ниже 👇🎬</b>",
                                 reply_markup=await get_channels_ikb(db),
                                 parse_mode='html')


@router.message(AddChannel.channel_id)
async def add_channel_id_cmd(message: Message, state: FSMContext):
    channel_id = message.text

    await message.answer("💬 Введите <b>название</b> канала: ", parse_mode='html')
    await state.set_state(AddChannel.channel_name)
    await state.update_data(channel_id=channel_id)


@router.message(AddChannel.channel_name)
async def add_channel_name_cmd(message: Message, state: FSMContext):
    channel_name = message.text

    await message.answer("🔗 Введите <b>ссылку</b> канала: ", parse_mode='html')
    await state.set_state(AddChannel.channel_link)
    await state.update_data(channel_name=channel_name)


@router.message(AddChannel.channel_link)
async def add_channel_link_cmd(message: Message, db: MongoDB, state: FSMContext):
    channel_link = message.text

    await state.update_data(channel_link=channel_link)

    data = await state.get_data()

    try:
        await db.channels.insert_one({
            "_id": data['channel_id'],
            "name": data['channel_name'],
            "link": data['channel_link']
        })

        await message.answer("<b>Канал</b> успешно добавлен ✅", reply_markup=admin_main_keyboard,
                             parse_mode='html')

        await state.clear()

    except DuplicateKeyError:
        await message.answer("Такой <b>канал</b> уже существует 🚫", parse_mode='html')

        await state.clear()


@router.message(F.text == "👨‍💻 Добавить фильм/сериал")
async def add_move_cmd(message: Message, state: FSMContext, db: MongoDB):
    if message.chat.type == "private":

        channels_id = await db.channels.distinct("_id")

        if await check_subscribe(channels_id, message.from_user.id, message):
            if message.from_user.id == ADMIN_ID:
                await message.answer("🆔 Введите <b>id</b> фильма/сериала: ",
                                     parse_mode='html',
                                     reply_markup=cancel_keyboard)
                await state.set_state(AddMovies.movies_id)
            else:
                await message.answer("Вы не админ 🚫",
                                     parse_mode='html')
        else:
            await message.answer("<b>Прежде чем начать пользоваться ботом, "
                                 "вы должны подписаться на все каналы ниже 👇🎬</b>",
                                 reply_markup=await get_channels_ikb(db),
                                 parse_mode='html')


@router.message(AddMovies.movies_id)
async def add_move_id_cmd(message: Message, state: FSMContext):
    movies_id = message.text

    await message.answer("💬 Введите <b>название</b> фильма/сериала: ", parse_mode='html')
    await state.set_state(AddMovies.movies_name)
    await state.update_data(movies_id=movies_id)


@router.message(AddMovies.movies_name)
async def add_move_name_cmd(message: Message, state: FSMContext):
    movies_name = message.text

    await message.answer("📄 Отправьте <b>описание</b> фильма/сериала: ", parse_mode='html')
    await state.set_state(AddMovies.movies_description)
    await state.update_data(movies_name=movies_name)


@router.message(AddMovies.movies_description)
async def add_move_name_cmd(message: Message, state: FSMContext):
    movies_description = message.text

    await message.answer("📷 Отправьте <b>фото</b> фильма/сериала: ", parse_mode='html')
    await state.set_state(AddMovies.movies_icon)
    await state.update_data(movies_description=movies_description)


@router.message(F.photo, AddMovies.movies_icon)
async def add_move_icon_cmd(message: Message, db: MongoDB, state: FSMContext):
    movies_icon = message.photo[-1]

    await state.update_data(movies_icon=movies_icon)

    data = await state.get_data()

    try:
        await db.movies.insert_one({
            "_id": data['movies_id'],
            "name": data['movies_name'],
            "description": data['movies_description'],
            "icon": {
                "file_id": movies_icon.file_id,
                "file_unique_id": movies_icon.file_unique_id,
                "width": movies_icon.width,
                "height": movies_icon.height,
                "file_size": movies_icon.file_size,
            }
        })

        movies = await db.movies.find_one({"_id": data['movies_id']})

        await message.bot.send_photo(
            chat_id=message.from_user.id,
            photo=movies_icon.file_id,
            caption=f"ID: <b>{movies['_id']}</b>\nНазвание: <b>{movies['name']}</b>\n\n"
                    f"Описание: <b>{movies['description']}</b>",
            parse_mode='html'
        )

        await message.answer("<b>Фильм/сериал</b> успешно добавлен ✅", reply_markup=admin_main_keyboard,
                             parse_mode='html')

        await state.clear()

    except DuplicateKeyError:
        await message.answer("Такой <b>фильм/сериал</b> уже существует 🚫", parse_mode='html')

        await state.clear()
