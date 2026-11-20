"""Identité injectée comme une session déjà vérifiée, jamais comme un paramètre HTTP."""
from .common import database, connect, check


def get_invoice(path, principal, invoice_id):
    with connect(path) as db:
        return db.execute("SELECT amount FROM invoices WHERE id=? AND owner=?",
                          (invoice_id, principal)).fetchone()


def run():
    with database("CREATE TABLE invoices(id TEXT PRIMARY KEY,owner TEXT,amount INTEGER);"
                  "INSERT INTO invoices VALUES('inv-a','alice',100),('inv-b','bob',900);") as path:
        own = get_invoice(path, "alice", "inv-a")
        other = get_invoice(path, "alice", "inv-b")
        injection = get_invoice(path, "alice", "' OR 1=1 --")
        check(own == (100,) and other is None and injection is None, "Fuite de facture")
    return {"naif": "SELECT par ID seul expose la facture de Bob",
            "facture_propre": own[0], "facture_bob": other, "injection": injection}
