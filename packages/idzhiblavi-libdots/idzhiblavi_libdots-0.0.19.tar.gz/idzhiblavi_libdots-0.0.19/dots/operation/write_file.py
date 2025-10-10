from dataclasses import dataclass

from dots.operation import Operation
from dots.operation.target import Target


@dataclass
class WriteFile(Operation):
    content: str  # or callable
    path: str

    async def apply(self, target: Target):
        if callable(self.content):
            content = self.content()
        else:
            content = self.content

        await target.write_file(
            content=content,
            path=self.path,
        )
