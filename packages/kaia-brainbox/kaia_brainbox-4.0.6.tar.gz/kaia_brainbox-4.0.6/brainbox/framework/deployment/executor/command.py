from typing import *
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Command:
    @dataclass
    class Options:
        workdir: str | Path | None = None
        return_output: bool = False
        ignore_exit_code: bool = False
        monitor_output: Optional[Callable[[str], None]] = None


    command: tuple[str,...]
    options: Optional['Command.Options'] = None

