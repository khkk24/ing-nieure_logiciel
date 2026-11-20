"""File SQLite bornée, ACK durable puis reprise après arrêt du consommateur."""
from .common import database, connect, check

SCHEMA = "CREATE TABLE jobs(id TEXT PRIMARY KEY, status TEXT);"


def submit(path, job_id, capacity=10):
    with connect(path) as db:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM jobs WHERE id=?", (job_id,)).fetchone():
            return 202
        pending = db.execute("SELECT count(*) FROM jobs WHERE status='pending'").fetchone()[0]
        if pending >= capacity:
            return 429
        db.execute("INSERT INTO jobs VALUES(?,'pending')", (job_id,))
        return 202


def run():
    with database(SCHEMA) as path:
        codes = [submit(path, f"job-{i}") for i in range(30)]
        # Le worker s'arrête : les connexions sont fermées, les jobs restent sur disque.
        with connect(path) as restarted_worker:
            restarted_worker.execute("UPDATE jobs SET status='done' WHERE status='pending'")
        with connect(path) as db:
            done = db.execute("SELECT count(*) FROM jobs WHERE status='done'").fetchone()[0]
        check(codes.count(202) == done == 10 and codes.count(429) == 20, "Admission incorrecte")
    return {"arrivees": 30, "acceptees_durables": done, "refusees_explicitement": 20,
            "naif": "file sans limite : mémoire et latence croissent"}
