from aiogram.filters.callback_data import CallbackData
from uuid import UUID


class AddRecForm(CallbackData, prefix="addrecform"):
    zone_id: str


class AddRec(CallbackData, prefix="addrec"):
    id: UUID


def write_id(key, **kwargs):
    global memory
    memory[key] = kwargs
