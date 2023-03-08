from CloudFlare import CloudFlare
import logging
from logging import INFO
import asyncio
import multiprocessing

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Text, Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

# Local imports
from Middleware import WhitelistMiddleware
from credentials import *
from replies import record_reply, main_reply, sure_reply
from Buttons import Buttons
from CallbackFactory import ListRecords, GetRecInfo, DelRecConfirm, memory, DelRec, AddRec
from States import DNSForm

# Tuples
full_fields = ('id', 'name', 'type', 'content', 'proxied', 'proxiable')
brief_fields = ('id', 'name', 'type')
main_buttons = ('DNS', 'WireGuard')

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
dp.message.outer_middleware(WhitelistMiddleware())

'''
    Commands
'''


@dp.message(Command(commands=['id', 'getid', 'get_id']))
async def send_id(message: Message) -> None:
    await message.reply(str(message.chat.id))


@dp.callback_query(Text(startswith="WireGuard"))
async def wg(callback: CallbackQuery) -> None:
    await bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id)
    await callback.message.edit_text('Заглушка', reply_markup=Buttons.main_menu())


'''
    DNS handlers
'''


@dns_router.callback_query(Text(startswith="DNS"))
async def list_domains(callback: CallbackQuery) -> None:
    await callback.message.edit_text('Your zones are:', reply_markup=Buttons.list_zones())


@dns_router.callback_query(ListRecords.filter())
async def list_recs_cb_handler(callback: CallbackQuery, callback_data: ListRecords) -> None:
    zone_id = callback_data.zone_id

    records = [{field: record[field] for field in brief_fields}
               for record in cf.zones.dns_records.get(zone_id)]

    await callback.message.edit_text('Click to configure record:',
                                     reply_markup=Buttons.list_recs(records, zone_id))
    await callback.answer()


@dns_router.callback_query(GetRecInfo.filter())
async def get_rec_info_cb_handler(callback: CallbackQuery, callback_data: GetRecInfo) -> None:
    mem_id = callback_data.id
    data = memory.get(mem_id)
    zone_id = data['zone_id']
    record_id = data['record_id']

    #record = [{field: record[field] for field in full_fields}
    #          for record in cf.zones.dns_records.get(zone_id)
    #          if record['id'] == record_id][0]

    records = cf.zones.dns_records.get(zone_id)
    record = {}
    for r in records:
        #nonlocal record
        if r['id'] == record_id:
            record = r
            break

    await callback.message.edit_text(text=record_reply(record),
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
    await state.set_data({'zone_id': zone_id})
    await callback.message.edit_text(text="Enter record you'd like to add",
                                     reply_markup=Buttons.return_to_recs(zone_id))


@dns_add_rec_form.message(DNSForm.rec_name)
async def add_rec_name_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(DNSForm.content)
    data = await state.get_data()
    data['name'] = message.text
    zone_id = data.get('zone_id')
    await state.set_data(data)
    await message.answer(f'Write record content:', reply_markup=Buttons.return_to_recs(zone_id))


@dns_add_rec_form.message(DNSForm.content)
async def add_rec_content_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(DNSForm.rec_type)
    data = await state.get_data()
    data['content'] = message.text
    zone_id = data.get('zone_id')
    await state.set_data(data)
    await message.answer(f'Write record type [A, CNAME, AAA, etc.]:', reply_markup=Buttons.return_to_recs(zone_id))


@dns_add_rec_form.message(DNSForm.rec_type)
async def add_rec_type_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    data['type'] = message.text
    rec_name = data['name']
    zone_id = data.pop('zone_id')
    try:
        cf.zones.dns_records.post(zone_id, data=data)
        await message.answer(f'Record "{rec_name}" successfully added!')
    except Exception as exc:
        await message.answer(f'Error: "{exc}"')
    await state.clear()


'''
    Main Menu
'''


@dp.message(Command(commands=['start', 'help', 'menu', 'home']))
async def send_welcome(message: Message) -> None:
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
