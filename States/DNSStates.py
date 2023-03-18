from aiogram.fsm.state import State, StatesGroup


class DNSForm(StatesGroup):
    rec_name = State()
    content = State()

