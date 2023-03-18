from aiogram.filters.callback_data import CallbackData
from uuid import UUID


class DelRec(CallbackData, prefix="delrec"):
    id: UUID


class DelRecConfirm(CallbackData, prefix="confdelrec"):
    id: UUID
