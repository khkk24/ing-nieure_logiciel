"""Fusion à trois versions ; conflits conservés pour décision humaine."""
from .common import check


def merge(base, left, right):
    merged, conflicts = {}, {}
    # Schéma fixe : la suppression de champs n'est pas gérée par ce POC.
    if not base.keys() == left.keys() == right.keys():
        raise ValueError("Schéma fixe requis")
    for key in base:
        a, b, initial = left[key], right[key], base[key]
        if a == b:
            merged[key] = a
        elif a == initial:
            merged[key] = b
        elif b == initial:
            merged[key] = a
        else:
            conflicts[key] = {"base": initial, "appareil_A": a, "appareil_B": b}
    return merged, conflicts


def run():
    base = {"title": "Visite", "city": "Lomé"}
    independent, none = merge(base, {**base, "title": "Contrôle"}, {**base, "city": "Accra"})
    partial, conflicts = merge(base, {**base, "title": "Contrôle"}, {**base, "title": "Audit"})
    check(independent == {"title": "Contrôle", "city": "Accra"} and not none, "Modification perdue")
    check("title" not in partial and conflicts["title"]["appareil_B"] == "Audit", "Conflit masqué")
    return {"fusion_independante": independent, "conflit_explicite": conflicts,
            "naif": "last-write-wins aurait supprimé silencieusement un titre"}
