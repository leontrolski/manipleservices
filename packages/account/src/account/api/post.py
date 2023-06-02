from typing import Protocol

from account import db, users


class NewUser(Protocol):
    name: str
    email: str


def add_user(user: NewUser) -> None:
    user = users.make_user(name=user.name, email=user.email)
    db.GLOBAL_USERS.append(user)
