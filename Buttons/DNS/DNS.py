from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from CloudFlare import CloudFlare
import uuid
from functools import lru_cache
# Local imports
from vars.credentials import EMAIL, CF_API_TOKEN

from CallbackFactory.DNS.AddRec import AddRecForm, AddRec
from CallbackFactory.DNS.DelRec import DelRecConfirm, DelRec
from CallbackFactory.DNS.Info import GetRecInfo, ListRecords

from CallbackFactory.Data.DNS import write_id, GetRecInfoData, AddRecData, DelRecData, DelRecConfirmData

# Tuples
main_buttons = ('DNS', 'WireGuard')
rec_types = ('A', 'AAAA', 'CNAME', 'PTR')

cf = CloudFlare(email=EMAIL, key=CF_API_TOKEN)


@lru_cache(maxsize=2)
def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in main_buttons:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))
    return builder.as_markup()


def list_zones() -> InlineKeyboardMarkup:
    zones_list = cf.zones.get()
    builder = InlineKeyboardBuilder()

    for zone in zones_list:
        callback_data = ListRecords(zone_id=zone['id'])
        builder.button(text=zone['name'], callback_data=callback_data)

    builder.row(InlineKeyboardButton(text='Main Menu', callback_data="menu"))
    return builder.as_markup()


def list_recs(records, zone_id) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for record in records:
        uniq_id = uuid.uuid4()
        data = GetRecInfoData(zone_id=zone_id, record_id=record['id'])
        write_id(key=uniq_id, data=data)
        callback_data = GetRecInfo(id=uniq_id)
        builder.button(text=f"{record['name']} {record['type']}", callback_data=callback_data)
    builder.adjust(1)
    add_rec_cb_data = AddRecForm(zone_id=zone_id)
    builder.row(InlineKeyboardButton(text='Add record', callback_data=add_rec_cb_data.pack()))

    builder.row(InlineKeyboardButton(text='Main Menu', callback_data="menu"),
                InlineKeyboardButton(text='Back', callback_data="DNS"))

    return builder.as_markup()


def get_rec_info(zone_id, record_id) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    uniq_id = uuid.uuid4()
    data = DelRecConfirmData(zone_id=zone_id, record_id=record_id)
    write_id(key=uniq_id, data=data)
    delete_rec_callback_data = DelRecConfirm(id=uniq_id).pack()
    back_callback_data = ListRecords(zone_id=zone_id).pack()
    builder.row(InlineKeyboardButton(text='Delete record', callback_data=delete_rec_callback_data),
                InlineKeyboardButton(text='Back', callback_data=back_callback_data))
    return builder.as_markup()


def return_to_recs(zone_id) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    back_callback_data = ListRecords(zone_id=zone_id)
    builder.button(text='Cancel', callback_data=back_callback_data)
    return builder.as_markup()


def rec_del_conf(zone_id, record_id) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    uniq_id = uuid.uuid4()
    data = DelRecData(zone_id=zone_id, record_id=record_id)
    write_id(key=uniq_id, data=data)
    del_rec_callback_data = DelRec(id=uniq_id).pack()
    canc_callback_data = ListRecords(zone_id=zone_id).pack()
    builder.row(InlineKeyboardButton(text='Delete record', callback_data=del_rec_callback_data),
                InlineKeyboardButton(text='Cancel', callback_data=canc_callback_data))
    return builder.as_markup()


def select_rec_type(data) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    zone_id = data.pop('zone_id')

    for rt in rec_types:
        uniq_id = uuid.uuid4()
        rec_data = data.copy()
        rec_data['type'] = rt
        data = AddRecData(zone_id=zone_id, data=rec_data)
        write_id(key=uniq_id, data=data)
        callback_data = AddRec(id=uniq_id).pack()
        builder.button(text=f"{rt}", callback_data=callback_data)
    builder.adjust(1)

    canc_callback_data = ListRecords(zone_id=zone_id).pack()
    builder.row(InlineKeyboardButton(text='Cancel', callback_data=canc_callback_data))

    return builder.as_markup()
