import CloudFlare
import logging
from logging import INFO
import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Text, Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

# My imports
from credentials import *
from replies import record_reply, main_reply, sure_reply
from functions import *
from Buttons import Buttons, ListRecords, GetRecInfo, DelRecConfirm

from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    add_rec = State()


# Configure logging
logging.basicConfig(level=INFO)

# Cloudflare https://github.com/cloudflare/python-cloudflare
cf = CloudFlare.CloudFlare(email=EMAIL, key=CF_API_TOKEN)

# Initialize bot and dispatcher 
bot = Bot(token=TG_API_TOKEN, parse_mode="HTML")
dp = Dispatcher()

form_router = Router()
dp.include_router(form_router)

'''
    Commands
'''


@dp.message(Command(commands=['id', 'getid', 'get_id']))
async def send_id(message: Message) -> None:
    await is_whitelisted(message.chat.id)
    await message.reply(str(message.chat.id))


@dp.callback_query(Text(startswith="WireGuard"))
async def wg(callback: CallbackQuery) -> None:
    await bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id)
    await callback.message.edit_text('Заглушка', reply_markup=Buttons.main_menu())


@dp.callback_query(Text(startswith="SSH"))
async def ssh(callback: CallbackQuery) -> None:
    await bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id)
    await callback.message.edit_text('Заглушка', reply_markup=Buttons.main_menu())


@dp.callback_query(Text(startswith="DNS"))
async def dns(callback: CallbackQuery) -> None:
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    zones_list = cf.zones.get()
    await callback.message.answer('Your zones are:', reply_markup=Buttons.list_zones(zones_list))


'''
    DNS handlers
'''


@dp.callback_query(ListRecords.filter())
async def list_recs_cb_handler(callback: CallbackQuery, state: FSMContext, callback_data: ListRecords) -> None:
    #record_id = callback_data.record_id
    zone_id = callback_data.zone_id
    #action = callback_data.action

    # Show zone's records ( if action is deleting, then show records after delete)
    #if action == 'del':
    ##    await cf.zones.dns_records.delete(zone_id, record_id)
    #    await callback.answer(text=f'Record successfully deleted!', show_alert=True)
    #elif action == 'add':
    #    await state.set_state(Form.add_rec)
    #    await callback.message.edit_text(text="Enter record you'd like to add", reply_markup=Buttons.add_rec(zone_id))
    #    await asyncio.sleep(10)

    parsed_output = await get_records(cf=cf, zone_id=zone_id, zone=True)

    await callback.message.edit_text('Click to configure record:',
                                     reply_markup=Buttons.list_records(parsed_output, zone_id))
    await callback.answer()


@dp.callback_query(GetRecInfo.filter())
async def get_rec_info_cb_handler(callback: CallbackQuery, callback_data: GetRecInfo) -> None:
    record_id = callback_data.record_id
    zone_id = callback_data.zone_id

    parsed_output = await get_records(cf=cf, zone_id=zone_id, record_id=record_id, zone=False)

    await callback.message.edit_text(text=record_reply(parsed_output[0]),
                                     reply_markup=Buttons.get_rec_info(zone_id, record_id=record_id))
    await callback.answer()


@form_router.message(Form.add_rec)
async def add_record(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.edit_text(f'Record "{message.text}" successfully added!')
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@dp.callback_query(DelRecConfirm.filter())
async def del_rec_conf_cb_handler(callback: CallbackQuery, callback_data: GetRecInfo) -> None:
    record_id = callback_data.record_id
    zone_id = callback_data.zone_id
    await callback.message.edit_text(text=sure_reply, reply_markup=Buttons.rec_del_conf(zone_id, record_id))
    await callback.answer()


'''
    Main Menu
'''


@dp.message(Command(commands=['start', 'help', 'menu', 'home']))
async def send_welcome(message: Message) -> None:
    await is_whitelisted(message.chat.id)
    await message.answer(main_reply, reply_markup=Buttons.main_menu())
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@dp.callback_query(Text(startswith='menu'))
async def menu_callback(callback: CallbackQuery) -> None:
    await callback.message.edit_text(main_reply, reply_markup=Buttons.main_menu())
    await callback.answer()


'''
    Main()
'''


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
