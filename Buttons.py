from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from vars import main_buttons
from aiogram.filters.callback_data import CallbackData



class ListRecords(CallbackData, prefix="zone"):
    zone_id: str


class GetRecInfo(CallbackData, prefix="rec"):
    zone_id: str
    record_id: str


class DelRecConfirm(CallbackData, prefix="rec"):
    zone_id: str
    record_id: str


class Buttons:
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for button in main_buttons:
            builder.add(InlineKeyboardButton(text=button, callback_data=button))
        return builder.as_markup()

    @staticmethod
    def list_zones(zones) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        print('start list zones')
        for zone in zones:
            callback_data = ListRecords(zone_id=zone['id'])
            builder.button(text=zone['name'],
                           callback_data=callback_data.pack())
        builder.row(InlineKeyboardButton(text='Main Menu', callback_data="menu"))
        print('end list zones')
        return builder.as_markup()

    @staticmethod
    def list_records(records, zone_id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for record in records:
            callback_data = GetRecInfo(zone_id=str(zone_id), record_id=str(record['id']))
            builder.row(InlineKeyboardButton(text=f"{record['name']} {record['type']}", callback_data=callback_data.pack()))

        add_record_callback_data = ListRecords(action='add', zone_id=zone_id)
        builder.row(InlineKeyboardButton(text='Add record', callback_data=add_record_callback_data))

        builder.row(InlineKeyboardButton(text='Main Menu', callback_data="menu"),
                    InlineKeyboardButton(text='Back', callback_data="DNS"))

        return builder.as_markup()

    @staticmethod
    def get_rec_info(zone_id, record_id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        delete_rec_callback_data = DelRecConfirm(zone_id=zone_id, record_id=record_id)
        back_callback_data = ListRecords(zone_id=zone_id)
        builder.row(InlineKeyboardButton(text='Delete record', callback_data=delete_rec_callback_data),
                    InlineKeyboardButton(text='Back', callback_data=back_callback_data))
        return builder.as_markup()

    @staticmethod
    def add_rec(zone_id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        back_callback_data = ListRecords(zone_id=zone_id)
        builder.button(text='Cancel', callback_data=back_callback_data)
        return builder.as_markup()

    @staticmethod
    def rec_del_conf(zone_id, record_id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        del_rec_callback_data = ListRecords(record_id=record_id, zone_id=zone_id, action='del')
        canc_callback_data = ListRecords(zone_id=zone_id)
        builder.row(InlineKeyboardButton(text='Delete record', callback_data=del_rec_callback_data),
                    InlineKeyboardButton(text='Cancel', callback_data=canc_callback_data))
        return builder.as_markup()
