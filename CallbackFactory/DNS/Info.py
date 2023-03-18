from aiogram.filters.callback_data import CallbackData
from uuid import UUID


class ListRecords(CallbackData, prefix="zone"):
    zone_id: str


class GetRecInfo(CallbackData, prefix="rec"):
    id: UUID
