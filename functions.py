from vars import whitelist, full_fields, brief_fields
from asyncio import CancelledError


async def is_whitelisted(chat_id):
    if chat_id not in whitelist:
        raise CancelledError


async def get_records(cf, zone_id, record_id=None, zone=True) -> list:
    zones = cf.zones.dns_records.get(zone_id)
    fields = brief_fields if zone else full_fields

    return [{field: record[field] for field in fields} for record in zones] if zone \
        else [{field: record[field] for field in fields} for record in zones if record['id'] == record_id]
