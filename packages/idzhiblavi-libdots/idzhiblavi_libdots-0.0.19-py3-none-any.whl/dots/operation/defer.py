from dots.operation import Operation, Target
from dots.util.run_sync import run_sync


class _Op(Operation):
    def __init__(self, awaitable):
        self._awaitable = awaitable

    async def apply(self, target: Target):
        op = await self._awaitable
        return await op.apply(target)


def defer(awaitable) -> Operation:
    return _Op(awaitable)
