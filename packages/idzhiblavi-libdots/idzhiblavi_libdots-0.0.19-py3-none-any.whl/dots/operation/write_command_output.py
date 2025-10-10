from dataclasses import dataclass

from dots.operation import Operation
from dots.operation.target import Target
from dots.util.run_command import run_command


@dataclass
class WriteCommandOutput(Operation):
    command: [str]
    path: str

    async def apply(self, target: Target):
        stdout, _, _ = await run_command(self.command)

        await target.write_file(
            content=stdout,
            path=self.path,
        )
