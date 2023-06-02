import datetime as dt

from account import users

from freezegun import freeze_time

now = dt.datetime(2022, 1, 1, tzinfo=dt.timezone.utc)


def test_make_user() -> None:
    with freeze_time(now):
        actual = users.make_user("Oli", "ojhrussell@gmail.com")

    assert actual == users.User(
        created=now,
        name="Oli",
        email="ojhrussell@gmail.com",
    )
