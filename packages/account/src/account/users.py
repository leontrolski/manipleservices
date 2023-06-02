import datetime as dt
from dataclasses import dataclass


@dataclass
class User:
    created: dt.datetime
    name: str
    email: str


def make_user(name: str, email: str) -> User:
    return User(
        created=dt.datetime.now(tz=dt.timezone.utc),
        name=name,
        email=email,
    )
