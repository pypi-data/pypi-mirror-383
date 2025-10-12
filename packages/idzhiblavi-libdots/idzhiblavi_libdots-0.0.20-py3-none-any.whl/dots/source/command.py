import subprocess

from dataclasses import dataclass, field
from dots.operation.write_command_output import WriteCommandOutput


@dataclass
class Command:
    command: [str]

    def write_to(self, path: str):
        return WriteCommandOutput(
            command=self.command,
            path=path,
        )
