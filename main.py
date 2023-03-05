from CloudFlare import CloudFlare
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
from Buttons import Buttons
from CallbackFactory import ListRecords, GetRecInfo, DelRecConfirm, memory, DelRec, AddRec
from States import DNSForm

# Configure logging
logging.basicConfig(level=INFO)

# Cloudflare https://github.com/cloudflare/python-cloudflare
cf = CloudFlare(email=EMAIL, key=CF_API_TOKEN)

# Initialize bot and dispatcher 
bot = Bot(token=TG_API_TOKEN, parse_mode="HTML")
dp = Dispatcher()

dns_add_rec_form = Router()
dns_router = Router()

dns_router.include_router(dns_add_rec_form)
dp.include_router(dns_router)

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


@dp.callback_query(Text(startswith="DNS"))
async def dns(callback: CallbackQuery) -> None:
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    await callback.message.answer('Your zones are:', reply_markup=Buttons.list_zones())


'''
    DNS handlers
'''


@dns_router.callback_query(ListRecords.filter())
async def list_recs_cb_handler(callback: CallbackQuery, callback_data: ListRecords) -> None:
    zone_id = callback_data.zone_id

    parsed_output = await get_records(cf=cf, zone_id=zone_id, zone=True)

    await callback.message.edit_text('Click to configure record:',
                                     reply_markup=Buttons.list_recs(parsed_output, zone_id))
    await callback.answer()


@dns_router.callback_query(GetRecInfo.filter())
async def get_rec_info_cb_handler(callback: CallbackQuery, callback_data: GetRecInfo) -> None:
    mem_id = callback_data.id
    data = memory.get(mem_id)
    zone_id = data['zone_id']
    record_id = data['record_id']

    parsed_output = await get_records(cf=cf, zone_id=zone_id, record_id=record_id, zone=False)

    await callback.message.edit_text(text=record_reply(parsed_output),
                                     reply_markup=Buttons.get_rec_info(zone_id=zone_id, record_id=record_id))
    await callback.answer()


@dns_router.callback_query(DelRecConfirm.filter())
async def del_rec_conf_cb_handler(callback: CallbackQuery, callback_data: DelRecConfirm) -> None:
    mem_id = callback_data.id
    data = memory.get(mem_id)
    zone_id = data['zone_id']
    record_id = data['record_id']

    await callback.message.edit_text(text=sure_reply, reply_markup=Buttons.rec_del_conf(zone_id, record_id))
    await callback.answer()


@dns_router.callback_query(DelRec.filter())
async def del_rec_cb_handler(callback: CallbackQuery, callback_data: DelRec) -> None:
    mem_id = callback_data.id
    data = memory.get(mem_id)
    zone_id = data['zone_id']
    record_id = data['record_id']

    cf.zones.dns_records.delete(zone_id, record_id)
    await callback.answer(text=f'Record successfully deleted!', show_alert=True)
    await list_recs_cb_handler(callback=callback, callback_data=ListRecords(zone_id=zone_id))


@dns_router.callback_query(AddRec.filter())
async def add_rec_conf_cb_handler(callback: CallbackQuery, callback_data: AddRec, state: FSMContext) -> None:
    zone_id = callback_data.zone_id
    await state.set_state(DNSForm.rec_name)
    await callback.message.edit_text(text="Enter record you'd like to add", reply_markup=Buttons.add_rec(zone_id))


@dns_add_rec_form.message(DNSForm.rec_name)
async def add_rec_name_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(DNSForm.content)
    await state.set_data({'record_name': message.text})
    await message.answer(f'Write record content:')
    #await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@dns_add_rec_form.message(DNSForm.content)
async def add_rec_content_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(DNSForm.rec_type)
    data = await state.get_data()
    data['content'] = message.text
    await state.set_data(data)
    await message.answer(f'Write record type [A, CNAME, AAA, etc.]:')
    #await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@dns_add_rec_form.message(DNSForm.rec_type)
async def add_rec_type_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    data = await state.get_data()
    rec_name = data['record_name']
    await message.answer(f'Record "{rec_name}" successfully added!')
    #await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)




'''
    dns_records = [
        {'name':'foo', 'type':'AAAA', 'content':'2001:d8b::1'},
        {'name':'foo', 'type':'A', 'content':'192.168.0.1'},
        {'name':'duh', 'type':'A', 'content':'10.0.0.1', 'ttl':120},
        {'name':'bar', 'type':'CNAME', 'content':'foo'},
        {'name':'shakespeare', 'type':'TXT', 'content':"What's in a name? That which we call a rose by any other name ..."}
    ]

    for dns_record in dns_records:
        r = cf.zones.dns_records.post(zone_id, data=dns_record)
'''

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
