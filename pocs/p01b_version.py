"""Modification concurrente d'un devis : compare-and-swap en base."""
from .common import database, connect, check


def update(path, expected, amount):
    with connect(path) as db:
        return db.execute("UPDATE quote SET amount=?, version=version+1 "
                          "WHERE id=1 AND version=?", (amount, expected)).rowcount == 1


def run():
    with database("CREATE TABLE quote(id INTEGER PRIMARY KEY, amount INTEGER, version INTEGER);"
                  "INSERT INTO quote VALUES(1,10000,1);") as path:
        first = update(path, 1, 12000)
        stale = update(path, 1, 9000)
        check(first and not stale, "Une modification obsolète doit être rejetée")
        with connect(path) as db:
            result = db.execute("SELECT amount,version FROM quote").fetchone()
        check(result == (12000, 2), "La première modification ne doit pas disparaître")
    return {"naif": "la dernière écriture aurait écrasé 12000 par 9000",
            "premiere_acceptee": first, "seconde_acceptee": stale,
            "montant_centimes": result[0], "version": result[1]}
