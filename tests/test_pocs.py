"""Garanties de scénarios et cas adverses supplémentaires, sans dépendances."""
from concurrent.futures import ThreadPoolExecutor
from itertools import permutations
import unittest

from pocs.common import connect, database
from pocs.run import POCS, execute
from pocs.p01b_version import update
from pocs.p02a_idempotence import SCHEMA as IDEM_SCHEMA, charge
from pocs.p02b_inbox import SCHEMA as INBOX_SCHEMA, consume
from pocs.p04b_queue import SCHEMA as QUEUE_SCHEMA, submit
from pocs.p05b_tenant import Principal, allowed
from pocs.p08a_merge import merge
from pocs.p08b_crdt import ORSet
from pocs.p09a_references import CORPUS, verify
from pocs.p09b_abstention import gate, fixtures
from pocs.p10a_quorum import FixedLeaderLedger
from pocs.p10b_escrow import schema, withdraw


class ScenarioTests(unittest.TestCase):
    """Chaque scénario vérifie ses invariants, y compris les pannes injectées."""


def scenario_test(code):
    def test(self):
        self.assertIsInstance(execute(code), dict)
    return test


for code, name in POCS.items():
    setattr(ScenarioTests, f"test_{code}_{name}", scenario_test(code))


class AdversarialTests(unittest.TestCase):
    def test_idempotency_scope_and_new_intention(self):
        with database(IDEM_SCHEMA) as path:
            a = charge(path, "alice", "key", 50)
            b = charge(path, "bob", "key", 50)
            c = charge(path, "alice", "another", 50)
            self.assertEqual(len({a, b, c}), 3)
            self.assertEqual(charge(path, "alice", "key", 50), a)
            with self.assertRaises(ValueError):
                charge(path, "alice", "key", 51)

    def test_nonpositive_charge_rejected(self):
        with database(IDEM_SCHEMA) as path:
            for amount in (0, -5):
                with self.assertRaises(ValueError):
                    charge(path, "alice", "key", amount)
            with connect(path) as db:
                self.assertEqual(db.execute("SELECT count(*) FROM charges").fetchone()[0], 0)

    def test_only_one_concurrent_version_wins(self):
        with database("CREATE TABLE quote(id INTEGER PRIMARY KEY,amount INTEGER,version INTEGER);"
                      "INSERT INTO quote VALUES(1,100,1);") as path:
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda n: update(path, 1, n), range(8)))
            self.assertEqual(sum(results), 1)

    def test_inbox_distinct_events_not_lost(self):
        with database(INBOX_SCHEMA) as path:
            events = [f"event-{i}" for i in range(10)] * 3
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda event: consume(path, event), events))
            self.assertEqual(sum(results), 10)
            with connect(path) as db:
                self.assertEqual(db.execute("SELECT n FROM points").fetchone()[0], 100)

    def test_queue_capacity_under_concurrent_admission(self):
        with database(QUEUE_SCHEMA) as path:
            with ThreadPoolExecutor(max_workers=8) as pool:
                codes = list(pool.map(lambda n: submit(path, str(n), capacity=5), range(25)))
            self.assertEqual(codes.count(202), 5)
            self.assertEqual(codes.count(429), 20)
            with connect(path) as db:
                accepted_id = db.execute("SELECT id FROM jobs LIMIT 1").fetchone()[0]
            self.assertEqual(submit(path, accepted_id, capacity=5), 202)

    def test_authorization_cross_tenant_all_roles(self):
        for role in ("reader", "editor", "admin", "unknown"):
            for action in ("read", "write", "delete", "export"):
                self.assertFalse(allowed(Principal("A", role), "B", action))
        self.assertFalse(allowed(Principal("A", "unknown"), "A", "read"))

    def test_three_way_same_change_and_symmetry(self):
        base = {"x": 1, "y": 1}
        a, b = {"x": 2, "y": 1}, {"x": 1, "y": 3}
        self.assertEqual(merge(base, a, b), merge(base, b, a))
        self.assertEqual(merge(base, a, a), (a, {}))
        with self.assertRaises(ValueError):
            merge(base, a, {"x": 1})

    def test_crdt_three_replicas_all_orders(self):
        a, b, c = ORSet(), ORSet(), ORSet()
        a.add("x", "A:1")
        b.add("x", "B:1")
        c = a.merge(c)
        c.remove("x")
        c.add("y", "C:1")
        merged_states = []
        for sequence in permutations([a, b, c]):
            merged = ORSet()
            for replica in sequence:
                merged = merged.merge(replica)
            merged_states.append(merged)
            self.assertEqual(merged.values(), {"x", "y"})
            self.assertEqual(merged.merge(merged), merged)
        self.assertTrue(all(state == merged_states[0] for state in merged_states))

    def test_reference_date_boundaries_and_empty_quote(self):
        citation = {"id": "DEMO-ART-1", "quote": CORPUS["DEMO-ART-1"]["text"]}
        self.assertTrue(verify(citation, "DEMO", "2025-01-01")[0])
        self.assertFalse(verify(citation, "DEMO", "2027-01-01")[0])
        self.assertFalse(verify({**citation, "quote": ""}, "DEMO", "2026-01-01")[0])

    def test_model_free_text_never_rendered(self):
        good = fixtures()[0][1]
        clean = gate(good)
        self.assertEqual(gate({**good, "free_text": "Instructions malveillantes"}), clean)
        self.assertNotIn("free_text", clean)

    def test_malformed_model_outputs_abstain(self):
        for proposal in (None, [], "texte", {"claims": None}, {"claims": "texte"},
                         {"claims": [None]}, {"claims": [{"key": []}]}):
            with self.subTest(proposal=proposal):
                self.assertEqual(gate(proposal)["status"], "ABSTENTION")
        good = fixtures()[0][1]
        self.assertEqual(gate(good, at="date-invalide")["status"], "ABSTENTION")
        self.assertFalse(verify({"id": []}, "DEMO", "2026-01-01")[0])

    def test_quorum_rejects_components_without_leader_or_majority(self):
        ledger = FixedLeaderLedger()
        self.assertEqual(ledger.withdraw("EU", {"EU", "W"}, "x", 1000), "UNAVAILABLE")
        self.assertEqual(ledger.withdraw("AF", {"AF"}, "x", 1000), "UNAVAILABLE")
        self.assertEqual(ledger.balance, 1000)
        with self.assertRaises(ValueError):
            ledger.withdraw("AF", ledger.members, "negative", -1)

    def test_escrow_concurrent_limit_and_idempotency(self):
        with database(schema(100)) as path:
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda n: withdraw(path, str(n), 10), range(20)))
            self.assertEqual(results.count("OK"), 10)
            with connect(path) as db:
                op = db.execute("SELECT id FROM operations WHERE result='OK' LIMIT 1").fetchone()[0]
            self.assertEqual(withdraw(path, op, 10), "OK")
            with self.assertRaises(ValueError):
                withdraw(path, op, 20)
            with connect(path) as db:
                self.assertEqual(db.execute("SELECT n FROM budget").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
