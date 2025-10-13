from dataclasses import dataclass
from ....framework import ConnectionSettings

@dataclass
class HelloBrainBoxSettings:
    connection = ConnectionSettings(20000, 5)
    setting: str = 'default_setting'
