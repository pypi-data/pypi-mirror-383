import asyncio


async def run_command(command: [str]):
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    return stdout.decode(), stderr.decode(), process.returncode
