"""Deux bases indépendantes : publication répétée après perte de l'accusé."""
from .common import database, connect, check

SOURCE = """
CREATE TABLE orders(id TEXT PRIMARY KEY);
CREATE TABLE outbox(id TEXT PRIMARY KEY, published INTEGER DEFAULT 0);
"""
TARGET = """
CREATE TABLE inbox(id TEXT PRIMARY KEY);
CREATE TABLE deliveries(id TEXT PRIMARY KEY);
"""


def create_order(path, fail=False):
    with connect(path) as db:
        db.execute("INSERT INTO orders VALUES('order-1')")
        if fail:
            raise RuntimeError("Crash avant insertion outbox")
        db.execute("INSERT INTO outbox(id) VALUES('order-1')")


def relay(source, target, lose_ack=False):
    with connect(source) as db:
        events = list(db.execute("SELECT id FROM outbox WHERE published=0"))
    for (event,) in events:
        with connect(target) as db:
            inserted = db.execute("INSERT OR IGNORE INTO inbox VALUES(?)", (event,)).rowcount
            if inserted:
                db.execute("INSERT INTO deliveries VALUES(?)", (event,))
        if lose_ack:
            raise RuntimeError("Destinataire validé, relais arrêté avant marquage")
        with connect(source) as db:
            db.execute("UPDATE outbox SET published=1 WHERE id=?", (event,))


def run():
    with database(SOURCE) as source, database(TARGET) as target:
        try:
            create_order(source, fail=True)
        except RuntimeError:
            pass
        with connect(source) as db:
            check(db.execute("SELECT count(*) FROM orders").fetchone()[0] == 0, "Dual write partiel")
        create_order(source)
        try:
            relay(source, target, lose_ack=True)
        except RuntimeError:
            pass
        relay(source, target)
        with connect(target) as db:
            count = db.execute("SELECT count(*) FROM deliveries").fetchone()[0]
        with connect(source) as db:
            pending = db.execute("SELECT count(*) FROM outbox WHERE published=0").fetchone()[0]
        check(count == 1 and pending == 0, "Événement perdu ou effet dupliqué")
    return {"publications_tentees": 2, "livraisons_creees": count, "outbox_en_attente": pending}
