from asyncio import create_subprocess_exec, create_subprocess_shell, subprocess
async def mediainfo(file: str, argument: str):
    process = await create_subprocess_shell(f'mediainfo "{argument}" "{file}"', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exitcode = await process.wait()
    stdout, stderr = await process.communicate()
    if exitcode is 0:
        return stdout.decode(), exitcode
    else:
        return stderr.decode(), exitcode

async def mkvmerge(output: str, arg: str, input: str):
    process = await create_subprocess_shell(f'mkvmerge -o "{output}" {arg} "{input}"', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exitcode = await process.wait()
    stdout, stderr = await process.communicate()
    if exitcode is 0:
        return stdout.decode(), exitcode
    else:
        return stderr.decode(), exitcode

async def mkvextract(input: str, arg: str, output: str):
    process = await create_subprocess_shell(f'mkvextract "{input}" {arg} "{output}"', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exitcode = await process.wait()
    stdout, stderr = await process.communicate()
    if exitcode is 0:
        return stdout.decode(), exitcode
    else:
        return stderr.decode(), exitcode