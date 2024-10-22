from typing import NamedTuple


class Task(NamedTuple):
    name: str
    description: str
    created_at: str
    updated_at: str
