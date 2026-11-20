"""Observed-remove set : ajout concurrent non observé conservé (add-wins)."""
from dataclasses import dataclass, field
from .common import check


@dataclass
class ORSet:
    adds: set = field(default_factory=set)
    removed: set = field(default_factory=set)

    def add(self, value, unique_tag):
        self.adds.add((value, unique_tag))

    def remove(self, value):
        self.removed |= {tag for item, tag in self.adds if item == value}

    def merge(self, other):
        return ORSet(self.adds | other.adds, self.removed | other.removed)

    def values(self):
        return {item for item, tag in self.adds if tag not in self.removed}


def run():
    initial = ORSet()
    initial.add("lait", "server:1")
    a, b = initial.merge(ORSet()), initial.merge(ORSet())
    a.remove("lait")
    b.add("lait", "phone-B:1")
    a.add("pain", "phone-A:1")
    ab, ba = a.merge(b), b.merge(a)
    check(ab == ba and ab.merge(ab) == ab, "Convergence ou idempotence violée")
    check(ab.values() == {"lait", "pain"}, "Sémantique add-wins incorrecte")
    return {"etat_A_hors_ligne": sorted(a.values()), "etat_B_hors_ligne": sorted(b.values()),
            "apres_fusion": sorted(ab.values()), "rejeu_sans_effet": ab.merge(b) == ab}
