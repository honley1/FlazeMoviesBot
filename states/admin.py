from aiogram.fsm.state import StatesGroup, State


class AddChannel(StatesGroup):
    channel_id = State()
    channel_name = State()
    channel_link = State()


class AddMovies(StatesGroup):
    movies_id = State()
    movies_name = State()
    movies_description = State()
    movies_icon = State()
