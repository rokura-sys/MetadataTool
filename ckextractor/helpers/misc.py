async def progress_call(current: int, total: int, message, action: str):
    percent = int(current/total*100)
    nmessg = f'{action}\nprogress = {percent}%'
    message.edit(nmessg)