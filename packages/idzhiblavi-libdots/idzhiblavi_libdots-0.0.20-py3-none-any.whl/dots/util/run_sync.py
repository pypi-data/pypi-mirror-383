import asyncio


def run_sync(future):
    return asyncio.run(future)
