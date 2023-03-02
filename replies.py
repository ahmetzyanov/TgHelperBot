def record_reply(data) -> str:
    return f'''Record: {data["name"]}
{data["type"]}\t{data["content"]}
{"Proxied: " + str(data["proxied"]) if bool(data["proxiable"]) else "Not proxiable"}'''


main_reply = "Привет"
sure_reply = 'Are you sure you want to delete record?'
