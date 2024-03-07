from aiogram.fsm.state import StatesGroup, State


class GetMovies(StatesGroup):
    movies_id = State()
