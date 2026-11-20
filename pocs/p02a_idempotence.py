"""Effet local et résultat persistés ensemble ; aucun vrai paiement externe."""
import hashlib
from concurrent.futures import ThreadPoolExecutor
from .common import database, connect, check

SCHEMA = """
CREATE TABLE requests(scope TEXT, key TEXT, hash TEXT, response TEXT,
                      PRIMARY KEY(scope,key));
CREATE TABLE charges(id INTEGER PRIMARY KEY, amount INTEGER CHECK(amount>0));
"""


def charge(path, scope, key, amount):
    if amount <= 0:
        raise ValueError("Montant positif requis")
    digest = hashlib.sha256(str(amount).encode()).hexdigest()
    with connect(path) as db:
        db.execute("BEGIN IMMEDIATE")
        saved = db.execute("SELECT hash,response FROM requests WHERE scope=? AND key=?",
                           (scope, key)).fetchone()
        if saved:
            if saved[0] != digest:
                raise ValueError("409 : même clé, contenu différent")
            return saved[1]
        row = db.execute("INSERT INTO charges(amount) VALUES(?)", (amount,))
        response = f"charge-{row.lastrowid}"
        db.execute("INSERT INTO requests VALUES(?,?,?,?)", (scope, key, digest, response))
        return response


def run():
    with database(SCHEMA) as path:
        # Le premier retour est volontairement ignoré : réponse réseau perdue après commit.
        charge(path, "alice:POST/charges", "achat-42", 500)
        with ThreadPoolExecutor(max_workers=12) as pool:
            replies = list(pool.map(lambda _: charge(path, "alice:POST/charges", "achat-42", 500), range(12)))
        mismatch = False
        try:
            charge(path, "alice:POST/charges", "achat-42", 900)
        except ValueError:
            mismatch = True
        with connect(path) as db:
            count = db.execute("SELECT count(*) FROM charges").fetchone()[0]
        check(count == 1 and len(set(replies)) == 1 and mismatch, "Déduplication incorrecte")
    return {"sans_cle": "13 tentatives pourraient créer 13 débits", "debits": count,
            "reponses_identiques": True, "contenu_different_rejete": mismatch}
