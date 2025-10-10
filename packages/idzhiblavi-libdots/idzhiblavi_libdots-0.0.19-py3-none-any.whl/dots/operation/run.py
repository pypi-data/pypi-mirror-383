from dataclasses import dataclass

from dots.operation import Operation
from dots.operation.target import Target


class _Run(Operation):
    def __init__(self, func, *args):
        self.func = func
        self.args = args

    async def apply(self, target: Target):
        self.func(*self.args)


def run(func, *args) -> Operation:
    return _Run(func, *args)
