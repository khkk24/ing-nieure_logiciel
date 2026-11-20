"""Modèle de routage/readiness, sans vrai réseau ni cluster Kubernetes."""
from dataclasses import dataclass
from .common import check


@dataclass
class Instance:
    version: str
    ready: bool
    draining: bool = False
    active: int = 0


def route(instances):
    return next((p for p in instances if p.ready and not p.draining), None)


def run():
    naive_gap = route([]) is None
    old = Instance("v1", True, active=1)
    new = Instance("v2", False)
    replicas = [old, new]
    routes = [route(replicas).version]
    # La nouvelle instance doit devenir prête AVANT de retirer l'ancienne.
    new.ready = True
    old.draining = True
    routes.append(route(replicas).version)
    check(old.active == 1, "Une requête en cours ne doit pas être tuée")
    old.active -= 1
    if old.active == 0:
        replicas.remove(old)
    routes.append(route(replicas).version)
    # Canary défectueux : rollback vers une version encore prête.
    fallback = Instance("v1", True)
    replicas.append(fallback)
    new.ready = False
    routes.append(route(replicas).version)
    check(routes == ["v1", "v2", "v2", "v1"], "Trou de disponibilité dans le modèle")
    return {"coupure_recreate": naive_gap, "routages": routes,
            "requete_ancienne_terminee": old.active == 0, "preuve": "modèle uniquement"}
