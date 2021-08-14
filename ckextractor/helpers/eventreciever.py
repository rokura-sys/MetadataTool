import os
import time
from telethon import Button
# from telethon.tl.functions.users import GetFullUserRequest
from json import loads

from .misc import progress_call
from .run import mediainfo, mkvmerge, mkvextract
from asyncio import get_event_loop
from .eventreciever import jobs

from helpers.FastTelethon import download_file, upload_file

async def start(event):
    await event.respond(
        """*Welcome to CK-Metadata-Bot!*

        if you are familiar with CK-Metadata-Tool,
        this is meant to be the Telegram bot version of that application.
        Yeah, but for now this will just be used to split streams only :(""")

async def help(event):
    await event.respond("no help for you! :(")

jobs = []

async def split(event):
    if not event.is_reply:
        await event.reply("you need to reply to a media document")
        return
    reply = event.get_reply_message()
    if not hasattr(reply.media, "document") or not reply.media.document.mime_type.startswith(("video","application/octet-stream")):
        await event.reply("only video documents!")
        return
    wdir = f"/WorkingDirectory/{event.chat_id}/"
    if not os.path.isdir(wdir):
        os.mkdir(wdir)
    prevjob = next((x for x in jobs if x.id == event.chat_id), None)
    if prevjob:
        await event.reply('First finish what you started')
        return
    online_file = reply.file
    file_path = wdir + online_file.name
    downloading_messg = event.reply(
        """Downloading...
        progress = 0%"""
        )
    with open(file_path, "wb") as streamwriter:
        await download_file(
            client=event.client,
            location=online_file,
            out=streamwriter,
            progress_callback=lambda recieved, total: get_event_loop().create_task(progress_call(current=recieved, total=total, message=downloading_messg, action='Downloading...'))
            )
    output, exitcode = mediainfo(file=file_path, argument='--output=JSON')
    if exitcode == 0:
        jObj = dict(loads(output))
        jObjTracks = jObj["media"]["track"]
        nbuttons = []
        orders = []
        for track in jObjTracks:
            if track["@type"] == "Video":
                order = track["StreamOrder"]
                data = f'{order}&/Video&/{file_path}&/{event.chat_id}'
                nbuttons.append([Button.inline(f'Video - {order}', data)])
            elif track["@type"] == "Audio":
                order = track["StreamOrder"]
                data = f'{order}&/Audio&/{file_path}&/{event.chat_id}'
                nbuttons.append([Button.inline(f'Audio - {order}', data)])
            elif track["@type"] == "Text":
                order = track["StreamOrder"]
                data = f'{order}&/Text&/{file_path}&/{event.chat_id}'
                nbuttons.append([Button.inline(f'Subtitle - {order}', data)])
            elif track["@type"] == "Menu":
                order = track["StreamOrder"]
                data = f'{order}&/Menu&/{file_path}&/{event.chat_id}'
                nbuttons.append([Button.inline(f'Chapter - {order}', data)])
            orders.append(order)
        nbuttons.append([Button.inline("All Streams", f"{orders}&/All&/{file_path}&/{event.chat_id}")])
        nbuttons.append([ 
            Button.inline("Done", f'/Done&/{file_path}&/{event.chat_id}'),
            Button.inline("Cancel", f'/Cancel&/{file_path}&/{event.chat_id}')
            ])
        await event.reply(text="Choose streams.", button=nbuttons)
        jobs.append(dict(id=event.chat_id, name='spliting' , button=nbuttons, Video=[], Audio=[], Text=[], Menu=[]))


async def SingleStream(event):
    order, type, path, id= event.data.split('&/')
    prevjob = next((x for x in jobs if x.id == event.chat_id), None)
    if not prevjob:
        await event.answer("something went wrong please start again", alert=True)
        time.sleep(3)
        await event.delete()
        return
    if id != event.chat_id:
        await event.answer("not your call")
        return
    prevjob[type].append(order)
    if prevjob["Path"] != path:
        prevjob["Path"] = path
    await event.edit(
        f"""Video = {prevjob["Video"]}
        Audio = {prevjob["Audio"]}
        Subtitles = {prevjob["Text"]}
        Chapter = {prevjob["Menu"]}""",
        button=prevjob["button"])


async def AllStreams(event):
    await event.answer("not implemented")

async def DoneOrCancel(event):
    type, path, id= event.data.split('&/')
    prevjob = next((x for x in jobs if x.id == event.chat_id), None)
    if not prevjob:
        await event.answer("something went wrong please start again", alert=True)
        time.sleep(3)
        await event.delete()
        return
    if id != event.chat_id:
        await event.answer("not your call")
        return
    if type == "Cancel":
        jobs.remove(prevjob)
        os.remove(path)
        await event.delete()
        return
    elif type == "Done":
        vlist = prevjob["Video"]
        alist = prevjob["Audio"]
        slist = prevjob["Text"]
        mlist = prevjob["Menu"]
        dir = os.path.dirname(path)
        extention = path.split(".")[-1]
        name = str(path.split("/")[-1]).removesuffix(f".{extention}")
        if vlist:
            upload_messg = await event.edit("Extracting Video...")
        for vid in vlist:
            newname = f'{vid} - Video - {name}.mkv'
            output = os.path.join(dir, newname)
            out, errorcode = await mkvmerge(output=output, arg=f"-v {vid}", input=path)
            if errorcode == 0:
                upload_messg = await upload_messg.edit(f"Uploading Video.../nStreamOrder = {vid}")
                with open(output, "rb") as streamreader:
                    result = await upload_file(
                        file=streamreader,
                        client=event.client,
                        name=newname,
                        progress_callback=lambda sent, total: get_event_loop().create_task(progress_call(current=sent, total=total,action=f"Uploading Video.../nStreamOrder = {vid}", message=upload_messg)))
                event.respond(file=result)
        if alist:
            upload_messg = await upload_messg.edit("Extracting Audio...")
        for aud in alist:
            newname = f'{aud} - Audio - {name}.mka'
            output = os.path.join(dir, newname)
            out, errorcode = await mkvmerge(output=output, arg=f"-v {aud}", input=path)
            if errorcode == 0:
                upload_messg = await upload_messg.edit(f"Uploading Audio.../nStreamOrder = {aud}")
                with open(output, "rb") as streamreader:
                    result = await upload_file(
                        file=streamreader,
                        client=event.client,
                        name=newname,
                        progress_callback=lambda sent, total: get_event_loop().create_task(progress_call(current=sent, total=total,action=f"Uploading Audio.../nStreamOrder = {aud}", message=upload_messg)))
                    event.respond(file=result)
        if slist:
            upload_messg = await upload_messg.edit("Extracting Subtitles...")
        for sub in slist:
            newname = f'{sub} - Subtitle - {name}.mks'
            output = os.path.join(dir, newname)
            out, errorcode = await mkvmerge(output=output, arg=f"-v {sub}", input=path)
            if errorcode == 0:
                upload_messg = await upload_messg.edit(f"Uploading Subtitle.../nStreamOrder = {sub}")
                with open(output, "rb") as streamreader:
                    result = await upload_file(
                        file=streamreader,
                        client=event.client,
                        name=newname,
                        progress_callback=lambda sent, total: get_event_loop().create_task(progress_call(current=sent, total=total,action=f"Uploading Subtitle.../nStreamOrder = {sub}", message=upload_messg)))
                    event.respond(file=result)
        if mlist:
            upload_messg = await upload_messg.edit("Extracting Chapter...")
            newname = f'Chapter - {name}.xml'
            output = os.path.join(dir, newname)
            out, errorcode = await mkvextract(input=path, arg="chapter", output=output)
            if errorcode == 0:
                upload_messg = await upload_messg.edit("Uploading Chapter...")
                with open(output, "rb") as streamreader:
                    result = await upload_file(
                        file=streamreader,
                        client=event.client,
                        name=newname,
                        progress_callback=lambda sent, total: get_event_loop().create_task(progress_call(current=sent, total=total,action='Uploading Chapter...', message=upload_messg)))
                    event.respond(file=result)
        await upload_messg.Delete()
                
