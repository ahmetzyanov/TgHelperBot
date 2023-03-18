from aiogram import Router
from aiogram.types import Message
from CloudFlare import CloudFlare
from aiogram.fsm.context import FSMContext
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
Content: {data['content']}
''', reply_markup=Buttons.select_rec_type(zone_id))


# @dns_add_rec_form.message(DNSForm.rec_type)
# async def add_rec_type_handler(message: Message, state: FSMContext) -> None:
#     data = await state.get_data()
#     data['type'] = message.text
#     rec_name = data['name']
#     zone_id = data.pop('zone_id')
#     try:
#         cf.zones.dns_records.post(zone_id, data=data)
#         await message.answer(f'Record "{rec_name}" successfully added!')
#     except Exception as exc:
#         await message.answer(f'Error: "{exc}"')
#     await state.clear()
