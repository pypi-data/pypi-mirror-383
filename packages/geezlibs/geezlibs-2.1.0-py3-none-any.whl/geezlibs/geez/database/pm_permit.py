from geezlibs.geez.database import db_x

def get_approved():
    return db_x.get_key("PMPERMIT") or []


def approve_user(id):
    ok = get_approved()
    if id in ok:
        return True
    ok.append(id)
    return db_x.set_key("PMPERMIT", ok)


def disapprove_user(id):
    ok = get_approved()
    if id in ok:
        ok.remove(id)
        return db_x.set_key("PMPERMIT", ok)


def is_approved(id):
    return id in get_approved()