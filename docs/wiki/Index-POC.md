# Les vingt POC

Depuis la racine du dépôt : `python3 -m pocs.run CODE`. Les commandes sont indépendantes et leurs données sont temporaires.

| Défi | POC | Code source | Commande |
|---|---|---|---|
| Concurrence | 01a — ticket | [Ouvrir](../../pocs/p01a_ticket.py) | `python3 -m pocs.run 01a` |
| Concurrence | 01b — version | [Ouvrir](../../pocs/p01b_version.py) | `python3 -m pocs.run 01b` |
| Idempotence | 02a — idempotence | [Ouvrir](../../pocs/p02a_idempotence.py) | `python3 -m pocs.run 02a` |
| Idempotence | 02b — inbox | [Ouvrir](../../pocs/p02b_inbox.py) | `python3 -m pocs.run 02b` |
| Résilience | 03a — transfer | [Ouvrir](../../pocs/p03a_transfer.py) | `python3 -m pocs.run 03a` |
| Résilience | 03b — breaker | [Ouvrir](../../pocs/p03b_breaker.py) | `python3 -m pocs.run 03b` |
| Scalabilité | 04a — cache | [Ouvrir](../../pocs/p04a_cache.py) | `python3 -m pocs.run 04a` |
| Scalabilité | 04b — queue | [Ouvrir](../../pocs/p04b_queue.py) | `python3 -m pocs.run 04b` |
| Sécurité | 05a — ownership | [Ouvrir](../../pocs/p05a_ownership.py) | `python3 -m pocs.run 05a` |
| Sécurité | 05b — tenant | [Ouvrir](../../pocs/p05b_tenant.py) | `python3 -m pocs.run 05b` |
| Fiabilité métier | 06a — outbox | [Ouvrir](../../pocs/p06a_outbox.py) | `python3 -m pocs.run 06a` |
| Fiabilité métier | 06b — saga | [Ouvrir](../../pocs/p06b_saga.py) | `python3 -m pocs.run 06b` |
| Déploiement | 07a — rollout | [Ouvrir](../../pocs/p07a_rollout.py) | `python3 -m pocs.run 07a` |
| Déploiement | 07b — migration | [Ouvrir](../../pocs/p07b_migration.py) | `python3 -m pocs.run 07b` |
| Synchronisation | 08a — merge | [Ouvrir](../../pocs/p08a_merge.py) | `python3 -m pocs.run 08a` |
| Synchronisation | 08b — crdt | [Ouvrir](../../pocs/p08b_crdt.py) | `python3 -m pocs.run 08b` |
| Fiabilité de l’IA | 09a — references | [Ouvrir](../../pocs/p09a_references.py) | `python3 -m pocs.run 09a` |
| Fiabilité de l’IA | 09b — abstention | [Ouvrir](../../pocs/p09b_abstention.py) | `python3 -m pocs.run 09b` |
| Systèmes distribués | 10a — quorum | [Ouvrir](../../pocs/p10a_quorum.py) | `python3 -m pocs.run 10a` |
| Systèmes distribués | 10b — escrow | [Ouvrir](../../pocs/p10b_escrow.py) | `python3 -m pocs.run 10b` |

## Tout vérifier

```bash
python3 -m pocs.run --all
python3 -m unittest discover -s tests -v
```

Pour les prérequis, les résultats attendus et les limites, suivre [le parcours](Parcours.md). Les scripts ne sont pas vingt services prêts à déployer : ils isolent vingt mécanismes, puis les cours proposent leurs extensions réelles.
