import CloudFlare
import logging
from logging import INFO

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Text, Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

# My imports
from credentials import *
from replies import record_reply, main_reply, sure_reply
from functions import *
from Buttons import Buttons
from CallbackData import CallbackData

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
    await callback.message.answer('Your zones are:', reply_markup=Buttons.dns(zones_list))


'''
    DNS handlers
'''


@dp.callback_query(Text(startswith="zone"))
async def zones_callback(callback: CallbackQuery, state: FSMContext) -> None:
    # callback_data = zone_<zone_id>, so we need to parse zone_id:
    transaction_id = callback.data.split('_')[1]
    data = CallbackData.get_from_memory(transaction_id)
    record_id = data['record_id']
    zone_id = data['zone_id']
    action = data['action']

    # Show zone's records ( if action is deleting, then show records after delete)
    if action == 'del':
        await cf.zones.dns_records.delete(zone_id, record_id)
        await callback.answer(text=f'Record successfully deleted!', show_alert=True)
    elif action == 'add':
        await state.set_state(Form.add_rec)
        await callback.message.answer(text="Enter record you'd like to add")
        raise CancelledError

    parsed_output = await get_records(cf=cf, zone_id=zone_id, zone=True)

    await callback.message.edit_text('Click to configure record:', reply_markup=Buttons.records(parsed_output, zone_id))
    await callback.answer()


@dp.callback_query(Text(startswith="rec_"))
async def record_callback(callback: CallbackQuery) -> None:
    transaction_id = callback.data.split('_')[1]
    data = CallbackData.get_from_memory(transaction_id)
    record_id = data['record_id']
    zone_id = data['zone_id']

    parsed_output = await get_records(cf=cf, zone_id=zone_id, record_id=record_id, zone=False)
    print(parsed_output)

    # Delete confirmation proceeding
    if data['action'] == 'confirm':
        await callback.message.edit_text(text=sure_reply, reply_markup=Buttons.confirmation(zone_id, record_id))
        await callback.answer()
        raise CancelledError

    await callback.message.edit_text(text=record_reply(parsed_output[0]),
                                     reply_markup=Buttons.record(zone_id, record_id=record_id))
    await callback.answer()


@form_router.message(Form.add_rec)
async def add_record(message: Message, state: FSMContext) -> None:
    print('debug')
    await state.clear()
    await message.answer(f'Record "{message.text}" successfully added!')


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


def main() -> None:
    dp.run_polling(bot)
    dp.include_router(form_router)


if __name__ == "__main__":
    main()
