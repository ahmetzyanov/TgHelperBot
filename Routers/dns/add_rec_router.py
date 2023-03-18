from aiogram import Router
from aiogram.types import Message, CallbackQuery
from CloudFlare import CloudFlare
from aiogram.fsm.context import FSMContext

from CallbackFactory import AddRec, memory
# Local imports
from States.DNSStates import DNSForm
from Buttons import Buttons
from vars.credentials import EMAIL, CF_API_TOKEN

dns_add_rec_form = Router()
cf = CloudFlare(email=EMAIL, key=CF_API_TOKEN)


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
    data = await state.get_data()
    data['content'] = message.text
    zone_id = data.get('zone_id')
    await message.answer(f'''Verify parameters you wrote and select record type.
Name: {data['name']}
Content: {data['content']}''', reply_markup=Buttons.select_rec_type(zone_id=zone_id, data=data))


@dns_add_rec_form.callback_query(AddRec.filter())
async def add_rec_type_handler(callback: CallbackQuery, callback_data: AddRec) -> None:
    mem_id = callback_data.id
    data = memory.get(mem_id)
    print(data)
    zone_id = data['zone_id']

    try:
        cf.zones.dns_records.post(zone_id, data=data['data'])
        await callback.message.answer(text='record added!', reply_markup=Buttons.return_to_recs(zone_id=zone_id))
    except Exception as exc:
        await callback.message.answer(text=str(exc), reply_markup=Buttons.return_to_recs(zone_id=zone_id))
    await callback.answer()

