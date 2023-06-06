from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class User:
    email: str


@dataclass(unsafe_hash=True)
class PWDHash:
    value: str
    user_id: int | None = None
