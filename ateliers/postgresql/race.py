"""Atelier explicite : réinitialise uniquement les tables ticket/sales du labo Compose."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess

COMPOSE = Path(__file__).with_name("compose.yaml")
BASE = ["docker", "compose", "-f", str(COMPOSE), "exec", "-T", "db", "psql",
        "-X", "-U", "lab", "-d", "defis_lab", "-v", "ON_ERROR_STOP=1", "-At", "-c"]


def sql(statement):
    return subprocess.run([*BASE, statement], check=True, capture_output=True,
                          text=True, timeout=30).stdout.strip()


def main():
    sql("""
    CREATE TABLE IF NOT EXISTS ticket(id integer PRIMARY KEY,quantity integer NOT NULL CHECK(quantity>=0));
    CREATE TABLE IF NOT EXISTS sales(id integer PRIMARY KEY,ticket_id integer REFERENCES ticket(id));
    TRUNCATE sales,ticket;
    INSERT INTO ticket VALUES(1,1);
    """)

    def buy(number):
        # Une instruction atomique : la vente ne naît que si la décrémentation réussit.
        return sql(f"""
        WITH reserved AS (
          UPDATE ticket SET quantity=quantity-1 WHERE id=1 AND quantity>0 RETURNING id
        ) INSERT INTO sales SELECT {number},id FROM reserved RETURNING id;
        """)

    with ThreadPoolExecutor(max_workers=20) as pool:
        list(pool.map(buy, range(20)))
    result = sql("SELECT quantity,(SELECT count(*) FROM sales) FROM ticket WHERE id=1;")
    if result != "0|1":
        raise AssertionError(f"Attendu stock=0 et ventes=1, obtenu {result!r}")
    print("OK PostgreSQL : 20 tentatives, une vente, stock final nul.")


if __name__ == "__main__":
    main()
