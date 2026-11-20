"""Deux lectures obsolètes, puis 24 vrais acheteurs concurrents en SQLite."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from .common import database, connect, check


def run():
    # Ordonnancement adversarial : les deux clients lisent avant toute écriture.
    stock = 1
    snapshots = [stock, stock]
    ventes_naives = sum(s > 0 for s in snapshots)
    with database("CREATE TABLE stock(id INTEGER PRIMARY KEY, n INTEGER CHECK(n>=0));"
                  "INSERT INTO stock VALUES(1,1);") as path:
        start = Barrier(24)

        def buy(_):
            start.wait(timeout=10)
            with connect(path) as db:
                return db.execute("UPDATE stock SET n=n-1 WHERE id=1 AND n>0").rowcount

        with ThreadPoolExecutor(max_workers=24) as pool:
            sold = sum(pool.map(buy, range(24)))
        with connect(path) as db:
            remaining = db.execute("SELECT n FROM stock").fetchone()[0]
        check(sold == 1 and remaining == 0, "Une seule vente doit être validée")
    return {"ventes_naives": ventes_naives, "acheteurs": 24,
            "ventes_atomiques": sold, "stock_final": remaining}
