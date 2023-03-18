from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from CloudFlare import CloudFlare
from aiogram.fsm.context import FSMContext

from CallbackFactory import AddRec, memory
# Local imports
from States.DNSStates import DNSForm
from Buttons import Buttons
from vars.credentials import EMAIL, CF_API_TOKEN, TG_API_TOKEN

dns_add_rec_form = Router()

bot = Bot(token=TG_API_TOKEN, parse_mode="HTML")
cf = CloudFlare(email=EMAIL, key=CF_API_TOKEN)


@dns_add_rec_form.message(DNSForm.rec_name)
async def add_rec_name_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(DNSForm.content)
    data = await state.get_data()
    data['name'] = message.text
    zone_id = data.get('zone_id')
    await state.set_data(data)
    await message.edit_text(f'Write record content:', reply_markup=Buttons.return_to_recs(zone_id))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@dns_add_rec_form.message(DNSForm.content)
async def add_rec_content_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    data['content'] = message.text
    await message.edit_text(f'''Verify parameters you wrote and select record type.
Name: {data['name']}
Content: {data['content']}''', reply_markup=Buttons.select_rec_type(data=data))
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@dns_add_rec_form.callback_query(AddRec.filter())
async def add_rec_type_handler(callback: CallbackQuery, callback_data: AddRec) -> None:
    mem_id = callback_data.id
    data = memory.get(mem_id)
    zone_id = data['zone_id']

    try:
        cf.zones.dns_records.post(zone_id, data=data['data'])
        await callback.answer(text='record added!', reply_markup=Buttons.return_to_recs(zone_id=zone_id), show_alert=True)
    except Exception as exc:
        await callback.answer(text=str(exc), reply_markup=Buttons.return_to_recs(zone_id=zone_id), show_alert=True)

