"""Saga persistée, trois bases ; orchestrateur unique, prestataires locaux simulés."""
from .common import database, connect, check

ORDERS = "CREATE TABLE orders(id TEXT PRIMARY KEY,state TEXT); INSERT INTO orders VALUES('o1','NEW');"
STOCK = "CREATE TABLE holds(id TEXT PRIMARY KEY,state TEXT);"
PAYMENTS = "CREATE TABLE payments(id TEXT PRIMARY KEY,state TEXT);"


class Saga:
    def __init__(self, orders, stock, payments):
        self.orders, self.stock, self.payments = orders, stock, payments

    def state(self):
        with connect(self.orders) as db:
            return db.execute("SELECT state FROM orders WHERE id='o1'").fetchone()[0]

    def save(self, state):
        with connect(self.orders) as db:
            db.execute("UPDATE orders SET state=? WHERE id='o1'", (state,))

    def resume(self, crash_after_payment=False, reject_confirmation=False, refund_down=False):
        if self.state() == "NEW":
            with connect(self.stock) as db:
                db.execute("INSERT OR IGNORE INTO holds VALUES('o1','HELD')")
            self.save("RESERVED")
        if self.state() == "RESERVED":
            with connect(self.payments) as db:
                db.execute("INSERT OR IGNORE INTO payments VALUES('o1','CAPTURED')")
            if crash_after_payment:
                raise RuntimeError("Paiement effectué, réponse perdue")
            self.save("PAID")
        if self.state() == "PAID":
            self.save("COMPENSATING" if reject_confirmation else "CONFIRMED")
        if self.state() == "COMPENSATING":
            if refund_down:
                raise TimeoutError("Remboursement indisponible, garder COMPENSATING")
            with connect(self.payments) as db:
                db.execute("UPDATE payments SET state='REFUNDED' WHERE id='o1'")
            with connect(self.stock) as db:
                db.execute("UPDATE holds SET state='RELEASED' WHERE id='o1'")
            self.save("CANCELLED")
        return self.state()


def run():
    with database(ORDERS) as orders, database(STOCK) as stock, database(PAYMENTS) as payments:
        saga = Saga(orders, stock, payments)
        try:
            saga.resume(crash_after_payment=True)
        except RuntimeError:
            pass
        recovered = Saga(orders, stock, payments).resume()
        with connect(payments) as db:
            count = db.execute("SELECT count(*) FROM payments").fetchone()[0]
        check(recovered == "CONFIRMED" and count == 1, "Double capture après reprise")
    with database(ORDERS) as orders, database(STOCK) as stock, database(PAYMENTS) as payments:
        saga = Saga(orders, stock, payments)
        try:
            saga.resume(reject_confirmation=True, refund_down=True)
        except TimeoutError:
            pass
        pending = saga.state()
        final = Saga(orders, stock, payments).resume()
        with connect(payments) as db:
            refunded = db.execute("SELECT state FROM payments").fetchone()[0]
        with connect(stock) as db:
            released = db.execute("SELECT state FROM holds").fetchone()[0]
        check((pending, final, refunded, released) ==
              ("COMPENSATING", "CANCELLED", "REFUNDED", "RELEASED"), "Compensation incomplète")
    return {"reprise": recovered, "captures": count, "pendant_panne_remboursement": pending,
            "apres_reprise": final, "paiement": refunded, "stock": released}
