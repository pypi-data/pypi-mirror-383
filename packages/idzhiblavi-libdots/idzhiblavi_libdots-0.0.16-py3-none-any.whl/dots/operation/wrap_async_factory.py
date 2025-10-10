from dots.operation import Operation, Target


class _Op(Operation):
    def __init__(self, awaitable):
        self._factory = factory

    async def apply(self, target: Target):
        op = await self._factory()
        return await op.apply(target)


def wrap_async_factory(factory) -> Operation:
    return _Op(factory)
