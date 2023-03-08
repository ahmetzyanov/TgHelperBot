from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from CloudFlare import CloudFlare
import uuid
from CallbackFactory import DelRecConfirm, GetRecInfo, ListRecords, write_id, DelRec, AddRec
from functools import lru_cache

from credentials import EMAIL, CF_API_TOKEN

cf = CloudFlare(email=EMAIL, key=CF_API_TOKEN)


class Buttons:
    @staticmethod
    @lru_cache(maxsize=50)
    def main_menu() -> InlineKeyboardMarkup:
        from main import main_buttons
        builder = InlineKeyboardBuilder()
        for button in main_buttons:
            builder.add(InlineKeyboardButton(text=button, callback_data=button))
        return builder.as_markup()

    @staticmethod
    def list_zones() -> InlineKeyboardMarkup:
        zones_list = cf.zones.get()
        builder = InlineKeyboardBuilder()

        for zone in zones_list:
            callback_data = ListRecords(zone_id=zone['id'])
            builder.button(text=zone['name'], callback_data=callback_data)

        builder.row(InlineKeyboardButton(text='Main Menu', callback_data="menu"))
        return builder.as_markup()

    @staticmethod
    def list_recs(records, zone_id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for record in records:
            uniq_id = str(uuid.uuid4())
            write_id(key=uniq_id, zone_id=zone_id, record_id=record['id'])
            callback_data = GetRecInfo(id=uniq_id)
            builder.button(text=f"{record['name']} {record['type']}", callback_data=callback_data)
        builder.adjust(1)
        add_rec_cb_data = AddRec(zone_id=zone_id)
        builder.row(InlineKeyboardButton(text='Add record', callback_data=add_rec_cb_data.pack()))

        builder.row(InlineKeyboardButton(text='Main Menu', callback_data="menu"),
                    InlineKeyboardButton(text='Back', callback_data="DNS"))

        return builder.as_markup()

    @staticmethod
    def get_rec_info(zone_id, record_id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        uniq_id = str(uuid.uuid4())
        write_id(key=uniq_id, zone_id=zone_id, record_id=record_id)
        delete_rec_callback_data = DelRecConfirm(id=uniq_id).pack()
        back_callback_data = ListRecords(zone_id=zone_id).pack()
        builder.row(InlineKeyboardButton(text='Delete record', callback_data=delete_rec_callback_data),
                    InlineKeyboardButton(text='Back', callback_data=back_callback_data))
        return builder.as_markup()

    @staticmethod
    def return_to_recs(zone_id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        back_callback_data = ListRecords(zone_id=zone_id)
        builder.button(text='Cancel', callback_data=back_callback_data)
        return builder.as_markup()

    @staticmethod
    def rec_del_conf(zone_id, record_id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        uniq_id = str(uuid.uuid4())
        write_id(key=uniq_id, zone_id=zone_id, record_id=record_id)
        del_rec_callback_data = DelRec(id=uniq_id).pack()
        canc_callback_data = ListRecords(zone_id=zone_id).pack()
        builder.row(InlineKeyboardButton(text='Delete record', callback_data=del_rec_callback_data),
                    InlineKeyboardButton(text='Cancel', callback_data=canc_callback_data))
        return builder.as_markup()
