from account import db, users


def user_by_email(email: str) -> users.User:
    matching = [u for u in db.GLOBAL_USERS if u.email == email]
    if len(matching) != 1:
        raise RuntimeError("Expected only one user")
    return matching[0]
