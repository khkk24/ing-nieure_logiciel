"""Livraison au moins une fois : inbox et effet dans la même transaction."""
from .common import database, connect, check

SCHEMA = """
CREATE TABLE inbox(consumer TEXT, event TEXT, PRIMARY KEY(consumer,event));
CREATE TABLE points(user TEXT PRIMARY KEY, n INTEGER);
INSERT INTO points VALUES('alice',0);
"""


def consume(path, event, fail=False):
    with connect(path) as db:
        added = db.execute("INSERT OR IGNORE INTO inbox VALUES('loyalty',?)", (event,)).rowcount
        if not added:
            return False
        if fail:
            raise RuntimeError("Crash après inscription inbox, avant effet")
        db.execute("UPDATE points SET n=n+10 WHERE user='alice'")
        return True


def run():
    with database(SCHEMA) as path:
        try:
            consume(path, "paid-1", fail=True)
        except RuntimeError:
            pass
        first = consume(path, "paid-1")
        repeated = consume(path, "paid-1")
        with connect(path) as db:
            points = db.execute("SELECT n FROM points").fetchone()[0]
        check(first and not repeated and points == 10, "Un seul effet métier attendu")
    return {"naif_points_deux_livraisons": 20, "points_apres_crash_et_rejeu": points}
