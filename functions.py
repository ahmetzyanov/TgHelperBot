from vars import full_fields, brief_fields


async def get_records(cf, zone_id, record_id=None, zone=True) -> list:
    zones = cf.zones.dns_records.get(zone_id)
    fields = brief_fields if zone else full_fields

    return [{field: record[field] for field in fields} for record in zones] if zone \
        else [{field: record[field] for field in fields} for record in zones if record['record_id'] == record_id][0]
