def record_reply(data) -> str:
    record_name = data['name']
    record_type = data['type']
    record_content = data['content']
    record_proxiable = bool(data['proxiable'])
    record_proxied = str(data['proxied'])

    reply = f'''Record: {record_name}
{record_type}\t{record_content}
{"Proxied: " + record_proxied if  record_proxiable else "Not proxiable"}'''

    return reply


main_reply = "Greeting, Boss"
sure_reply = 'Are you sure you want to delete record?'
