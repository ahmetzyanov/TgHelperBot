from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

# Local imports
from States.DNSStates import DNSForm
from Buttons import Buttons
from CloudFlare import CloudFlare
from vars.credentials import EMAIL, CF_API_TOKEN
from vars.replies import record_reply, sure_reply
from CallbackFactory import ListRecords, GetRecInfo, DelRecConfirm, memory, DelRec, AddRecForm


dns_router = Router()

# Cloudflare https://github.com/cloudflare/python-cloudflare
cf = CloudFlare(email=EMAIL, key=CF_API_TOKEN)

# Tuples
full_fields = ('id', 'name', 'type', 'content', 'proxied', 'proxiable')
brief_fields = ('id', 'name', 'type')


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
    zone_id = data.get('zone_id')
    record_id = data.get('record_id')

    records = cf.zones.dns_records.get(zone_id)
    record = {}
    for r in records:
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
    zone_id = data.get('zone_id')
    record_id = data.get('record_id')

    await callback.message.edit_text(text=sure_reply, reply_markup=Buttons.rec_del_conf(zone_id, record_id))
    await callback.answer()


@dns_router.callback_query(DelRec.filter())
async def del_rec_cb_handler(callback: CallbackQuery, callback_data: DelRec) -> None:
    mem_id = callback_data.id
    data = memory.get(mem_id)
    zone_id = data.get('zone_id')
    record_id = data.get('record_id')

    cf.zones.dns_records.delete(zone_id, record_id)
    await callback.answer(text=f'Record successfully deleted!', show_alert=True)
    await list_recs_cb_handler(callback=callback, callback_data=ListRecords(zone_id=zone_id))


@dns_router.callback_query(AddRecForm.filter())
async def add_rec_conf_cb_handler(callback: CallbackQuery, callback_data: AddRecForm, state: FSMContext) -> None:
    zone_id = callback_data.zone_id
    await state.set_state(DNSForm.rec_name)
    await state.set_data({'zone_id': zone_id})
    await callback.message.edit_text(text="Enter record you'd like to add",
                                     reply_markup=Buttons.return_to_recs(zone_id))
