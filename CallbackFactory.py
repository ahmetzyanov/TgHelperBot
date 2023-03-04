from aiogram.filters.callback_data import CallbackData


class ListRecords(CallbackData, prefix="zone"):
    zone_id: str


class GetRecInfo(CallbackData, prefix="rec"):
    id: str


class DelRecConfirm(CallbackData, prefix="confdelrec"):
    id: str


class DelRec(CallbackData, prefix="delrec"):
    id: str


class AddRec(CallbackData, prefix="addrec"):
    zone_id: str


memory = {}


def write_id(key, **kwargs):
    global memory
    memory[key] = kwargs
