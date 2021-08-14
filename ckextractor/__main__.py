import re, os, telethon

from telethon import TelegramClient, events
# from telethon.tl.functions.users import GetFullUserRequest
from helpers import eventreciever


APP_ID = int(os.environ.get("APP_ID", 12345))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
# ADMIN_GROUP = int(os.environ.get("ADMIN_GROUP", 12345))
try:
    client = TelegramClient("bot", APP_ID, API_HASH).start(bot_token=BOT_TOKEN)
except Exception as e:
    print(e)
    exit()


@client.on(events.NewMessage(pattern="/start"))
async def _(event):
    await eventreciever.start(event)


@client.on(events.NewMessage(pattern="/help"))
async def _(event):
    await eventreciever.help(event)


@client.on(events.NewMessage(pattern="/split_everything"))
async def _(event):
    await eventreciever.split(event)


@client.on(events.callbackquery.CallbackQuery(data=re.compile("/video&|/Text&|/Menu&|/Audio&")))
async def _(event):
    await eventreciever.SingleStream(event)


@client.on(events.callbackquery.CallbackQuery(data=re.compile("/All&")))
async def _(event):
    await eventreciever.AllStreams(event)


@client.on(events.callbackquery.CallbackQuery(data=re.compile("/Done&|/Cancel&")))
async def _(event):
    await eventreciever.DoneOrCancel(event)

client.run_until_disconnected()
