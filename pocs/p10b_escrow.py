"""Deux budgets régionaux durables préalloués, sans partage pendant les retraits."""
from .common import database, connect, check


def schema(amount):
    return f"""
    CREATE TABLE budget(id INTEGER PRIMARY KEY,n INTEGER CHECK(n>=0));
    INSERT INTO budget VALUES(1,{amount});
    CREATE TABLE operations(id TEXT PRIMARY KEY, amount INTEGER, result TEXT);
    """


def withdraw(path, op, amount):
    if amount <= 0:
        raise ValueError("Montant positif requis")
    with connect(path) as db:
        db.execute("BEGIN IMMEDIATE")
        existing = db.execute("SELECT amount,result FROM operations WHERE id=?", (op,)).fetchone()
        if existing:
            if existing[0] != amount:
                raise ValueError("Conflit idempotence")
            return existing[1]
        changed = db.execute("UPDATE budget SET n=n-? WHERE id=1 AND n>=?", (amount, amount)).rowcount
        result = "OK" if changed else "REGIONAL_LIMIT"
        db.execute("INSERT INTO operations VALUES(?,?,?)", (op, amount, result))
        return result


def run():
    with database(schema(600)) as africa, database(schema(400)) as europe:
        too_large = [withdraw(africa, "a1", 1000), withdraw(europe, "b1", 1000)]
        local = [withdraw(africa, "a2", 600), withdraw(europe, "b2", 400)]
        replay = withdraw(africa, "a2", 600)
        balances = []
        for path in (africa, europe):
            with connect(path) as db:
                balances.append(db.execute("SELECT n FROM budget").fetchone()[0])
        check(too_large == ["REGIONAL_LIMIT"] * 2 and local == ["OK"] * 2
              and replay == "OK" and balances == [0, 0], "Budget global dépassé")
    return {"budgets_initiaux": [600, 400], "retraits_1000": too_large,
            "retraits_600_et_400": local, "total_depense": 1000, "restant": sum(balances)}
