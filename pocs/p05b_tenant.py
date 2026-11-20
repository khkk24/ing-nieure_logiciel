"""Autorisation par organisation, rôle et action ; défense serveur pure."""
from dataclasses import dataclass
from .common import check


@dataclass(frozen=True)
class Principal:
    tenant: str
    role: str


def allowed(principal, resource_tenant, action):
    grants = {"reader": {"read"}, "editor": {"read", "write"}, "admin": {"read", "write", "delete"}}
    return principal.tenant == resource_tenant and action in grants.get(principal.role, set())


def run():
    admin = Principal("clinic-A", "admin")
    reader = Principal("clinic-A", "reader")
    decisions = {"admin_local": allowed(admin, "clinic-A", "delete"),
                 "admin_autre_tenant": allowed(admin, "clinic-B", "read"),
                 "lecteur_suppression": allowed(reader, "clinic-A", "delete"),
                 "action_inconnue": allowed(admin, "clinic-A", "export_secrets")}
    check(decisions == {"admin_local": True, "admin_autre_tenant": False,
                        "lecteur_suppression": False, "action_inconnue": False}, "Politique trop large")
    return {"naif": "le rôle admin seul autoriserait toutes les organisations", **decisions}
