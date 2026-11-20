"""Arrêt brutal d'un sous-processus avant/après COMMIT d'un virement local."""
import subprocess
import sys
from .common import database, connect, check

SCHEMA = """
CREATE TABLE accounts(id TEXT PRIMARY KEY, cents INTEGER CHECK(cents>=0));
INSERT INTO accounts VALUES('A',10000),('B',0);
CREATE TABLE transfers(id TEXT PRIMARY KEY);
"""
CHILD = """
import os, sqlite3, sys
c=sqlite3.connect(sys.argv[1])
c.execute('BEGIN IMMEDIATE')
c.execute("INSERT INTO transfers VALUES('t1')")
c.execute("UPDATE accounts SET cents=cents-1000 WHERE id='A'")
if sys.argv[2]=='before': os._exit(23)
c.execute("UPDATE accounts SET cents=cents+1000 WHERE id='B'")
c.commit()
os._exit(23)
"""


def snapshot(path):
    with connect(path) as db:
        return dict(db.execute("SELECT id,cents FROM accounts"))


def run():
    with database(SCHEMA) as path:
        before = subprocess.run([sys.executable, "-c", CHILD, str(path), "before"], check=False)
        rollback = snapshot(path)
        after = subprocess.run([sys.executable, "-c", CHILD, str(path), "after"], check=False)
        committed = snapshot(path)
        check(before.returncode == after.returncode == 23, "Le crash doit réellement avoir lieu")
        check(rollback == {"A": 10000, "B": 0}, "Débit partiel après crash")
        check(committed == {"A": 9000, "B": 1000}, "Commit perdu après arrêt du processus")
    return {"naif_total_apres_debit_seul": 9000, "avant_commit": rollback,
            "apres_commit": committed, "total_centimes": sum(committed.values())}
