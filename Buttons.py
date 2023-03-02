from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from vars import main_buttons
from CallbackData import CallbackData as cb


class Buttons:
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for button in main_buttons:
            builder.add(InlineKeyboardButton(text=button, callback_data=button))
        return builder.as_markup()

    @staticmethod
    def dns(zones) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for zone in zones:
            callback_data = cb(prefix='zone', zone_id=zone['id'])
            builder.button(text=zone['name'],
                           callback_data=callback_data())
        builder.row(InlineKeyboardButton(text='Main Menu', callback_data="menu"))
        return builder.as_markup()

    @staticmethod
    def records(records, zone_id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        for record in records:
            callback_data = cb(prefix='rec', zone_id=zone_id, record_id=record['id'])
            builder.row(InlineKeyboardButton(text=f"{record['name']} {record['type']}", callback_data=callback_data()))

        add_record_callback_data = cb(prefix='zone', action='add', zone_id=zone_id)
        builder.row(InlineKeyboardButton(text='Add record', callback_data=add_record_callback_data()))

        builder.row(InlineKeyboardButton(text='Main Menu', callback_data="menu"),
                    InlineKeyboardButton(text='Back', callback_data="DNS"))

        return builder.as_markup()

    @staticmethod
    def record(zone_id, record_id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        delete_rec_callback_data = cb(prefix='rec', zone_id=zone_id, record_id=record_id, action='confirm')
        back_callback_data = cb(prefix='zone', zone_id=zone_id)
        builder.row(InlineKeyboardButton(text='Delete record', callback_data=delete_rec_callback_data()),
                    InlineKeyboardButton(text='Back', callback_data=back_callback_data()))
        return builder.as_markup()

    @staticmethod
    def add_rec(zone_id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        back_callback_data = cb(prefix='zone', zone_id=zone_id)
        builder.button(InlineKeyboardButton(text='Back', callback_data=back_callback_data()))
        return builder.as_markup()

    @staticmethod
    def confirmation(zone_id, record_id) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        del_rec_callback_data = cb(prefix='zone', record_id=record_id, zone_id=zone_id, action='del')
        canc_callback_data = cb(prefix='zone', zone_id=zone_id)
        builder.row(InlineKeyboardButton(text='Delete record', callback_data=del_rec_callback_data()),
                    InlineKeyboardButton(text='Cancel', callback_data=canc_callback_data()))
        return builder.as_markup()
