from dataclasses import dataclass
from ...messaging import IMessage


@dataclass
class State(IMessage):
    user: str|None = None
    character: str|None = None
    activity: str|None = None
    language: str|None = None