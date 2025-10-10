from dots.operation import Operation
from dots.operation.target import Target


class _Noop(Operation):
    async def apply(self, target: Target):
        pass


def noop() -> Operation:
    return _Noop()
