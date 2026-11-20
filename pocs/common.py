"""Utilitaires locaux : une connexion par opération, données temporaires."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3
import tempfile


@contextmanager
def database(schema):
    with tempfile.TemporaryDirectory(prefix="defis-") as folder:
        path = Path(folder) / "lab.db"
        with connect(path) as db:
            db.executescript(schema)
        yield path


@contextmanager
def connect(path):
    db = sqlite3.connect(path, timeout=10)
    try:
        with db:
            yield db
    finally:
        db.close()


def check(condition, message):
    # Contrairement à assert, reste actif avec python -O.
    if not condition:
        raise AssertionError(message)
