"""Modèle à leader fixe : illustre l'indisponibilité en minorité, pas Raft complet."""
from .common import check


class FixedLeaderLedger:
    def __init__(self):
        self.members = {"AF", "EU", "W"}
        self.leader = "AF"
        self.balance = 1000
        self.results = {}

    def withdraw(self, caller, reachable_component, op_id, amount):
        if amount <= 0:
            raise ValueError("Montant positif requis")
        # La composante est fournie par le simulateur, jamais par un client réel.
        component = set(reachable_component) & self.members
        if caller not in component or self.leader not in component or len(component) < 2:
            return "UNAVAILABLE"
        if op_id in self.results:
            old_amount, result = self.results[op_id]
            if old_amount != amount:
                raise ValueError("Identifiant réutilisé avec un autre montant")
            return result
        result = "OK" if self.balance >= amount else "INSUFFICIENT"
        if result == "OK":
            self.balance -= amount
        self.results[op_id] = (amount, result)
        return result


def run():
    ledger = FixedLeaderLedger()
    majority = ledger.withdraw("AF", {"AF", "W"}, "withdraw-A", 1000)
    isolated = ledger.withdraw("EU", {"EU"}, "withdraw-B", 1000)
    after_heal = ledger.withdraw("EU", {"AF", "EU", "W"}, "withdraw-B", 1000)
    replay = ledger.withdraw("AF", {"AF", "EU", "W"}, "withdraw-A", 1000)
    check((majority, isolated, after_heal, replay, ledger.balance) ==
          ("OK", "UNAVAILABLE", "INSUFFICIENT", "OK", 0), "Double retrait")
    return {"naif_deux_copies": "deux retraits de 1000 seraient acceptés",
            "majorite": majority, "minorite": isolated, "apres_reseau": after_heal,
            "solde": ledger.balance, "limite": "pas d'élection, réplication ni panne du leader simulée"}
