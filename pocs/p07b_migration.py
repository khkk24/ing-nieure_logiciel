"""Migration expand/contract SQLite avec anciennes et nouvelles écritures."""
from .common import database, connect, check


def run():
    with database("CREATE TABLE users(id INTEGER PRIMARY KEY,name TEXT NOT NULL);"
                  "INSERT INTO users VALUES(1,'Alice');") as path:
        with connect(path) as db:
            db.executescript("""
            ALTER TABLE users ADD COLUMN display_name TEXT;
            CREATE TRIGGER old_insert AFTER INSERT ON users BEGIN
              UPDATE users SET display_name=NEW.name WHERE id=NEW.id;
            END;
            CREATE TRIGGER old_update AFTER UPDATE OF name ON users BEGIN
              UPDATE users SET display_name=NEW.name WHERE id=NEW.id;
            END;
            """)
            # La nouvelle lecture supporte le backfill incomplet.
            before = db.execute("SELECT COALESCE(display_name,name) FROM users").fetchone()[0]
            db.execute("UPDATE users SET display_name=name WHERE display_name IS NULL")
            db.execute("UPDATE users SET name='Alice v1' WHERE id=1")
            after_old_write = db.execute("SELECT display_name FROM users").fetchone()[0]
            # v2 fait une double écriture tant que v1 peut encore être utilisée.
            db.execute("UPDATE users SET name=?,display_name=? WHERE id=1", ("Alice v2", "Alice v2"))
            old_read = db.execute("SELECT name FROM users").fetchone()[0]
            # Contract : ici on suppose v1 retirée et sa fenêtre de rollback terminée.
            db.executescript("DROP TRIGGER old_insert; DROP TRIGGER old_update; ALTER TABLE users DROP COLUMN name;")
            final = db.execute("SELECT display_name FROM users").fetchone()[0]
        check((before, after_old_write, old_read, final) ==
              ("Alice", "Alice v1", "Alice v2", "Alice v2"), "Incompatibilité de schéma")
    return {"avant_backfill": before, "ecriture_v1_visible_v2": after_old_write,
            "ecriture_v2_visible_v1": old_read, "apres_contract": final}
