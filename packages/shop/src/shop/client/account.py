import datetime as dt
from dataclasses import dataclass

from account.api import get, post


@dataclass
class NewUser:
    name: str
    email: str


@dataclass
class User:
    created: dt.datetime
    name: str
    email: str


def add_user_then_retrieve(user: NewUser) -> User:
    post.add_user(user)
    added_user = get.user_by_email(user.email)

    return User(
        created=added_user.created,
        name=added_user.name,
        email=added_user.email,
    )
