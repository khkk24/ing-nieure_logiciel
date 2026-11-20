# Projet final — Plateforme de réservation avec agents de terrain

Ce document est le cahier des charges d'une extension à construire après les cours. La plateforme complète n'est pas déjà implémentée par les vingt scripts.

## Produit

Un organisateur propose des événements à capacité limitée. Les clients réservent et consultent leurs commandes. Les agents de terrain gèrent des fiches hors ligne. Un assistant documentaire explique les règles internes en citant des documents validés. Le paiement utilise d'abord un simulateur, puis éventuellement un environnement de test explicite.

## Étapes et critères d'acceptation

| Étape | Fonctionnalité | Critère observable |
|---|---|---|
| 1 | Réservation concurrente | Sur 100 demandes pour 10 places, au plus 10 confirmations et stock jamais négatif |
| 2 | Commande rejouable | 20 reprises d'une intention produisent une seule commande et le même résultat contractuel |
| 3 | Reprise après panne | Crash avant/après commit : aucun transfert local partiel, état inconnu rapprochable |
| 4 | API privée | Un utilisateur et un admin d'une autre organisation échouent sur lecture, mutation et export |
| 5 | Événements et saga | Crash à chaque frontière, puis reprise vers un état autorisé ou visible en attente |
| 6 | Capacité | Profil de trafic documenté, file bornée, aucune demande durablement acceptée oubliée |
| 7 | Livraison continue | Trafic mesuré pendant le rollout et compatibilité v1/v2 du schéma démontrée |
| 8 | Hors-ligne | Changements indépendants fusionnés, conflit métier visible, replay sans duplication |
| 9 | Régions | Partition : pas de dépense au-delà des droits, comportement indisponible explicitement testé |
| 10 | Assistant documentaire | Références vérifiées, interprétations distinguées, abstention évaluée sur cas adverses |

## Schéma de données de départ

- `events`, `inventory`, `reservations` avec capacité et version.
- `orders`, `payment_operations`, `idempotency_records` avec identifiants uniques.
- `outbox`, `consumer_inbox`, `workflow_states` pour reprise et transmission.
- `organizations`, `memberships`, `permissions` pour les frontières d'accès.
- `field_documents`, `document_operations`, `conflicts` pour la synchronisation.
- `sources`, `source_versions`, `passages`, `answer_evaluations` pour les preuves IA.

Ne pas transformer cette liste en microservices automatiquement. Commencer dans une base et un code modulaire, puis isoler uniquement les responsabilités nécessaires aux expériences distribuées.

## API indicative

```text
POST /reservations           Idempotency-Key ; identité vérifiée
GET  /operations/{id}         consultation d'un résultat encore inconnu
GET  /orders/{id}             autorisation sur la commande
POST /field-documents/sync    version de base + opérations identifiées
POST /assistant/questions    contexte + périmètre documentaire
GET  /health/ready            capacité à recevoir du trafic
```

## Évaluation

Pour chaque étape, attribuer 0 à 3 : 0 absent ; 1 explication seule ; 2 expérience locale reproductible ; 3 service réel testé avec panne et limites documentées. Une somme élevée ne remplace pas les invariants critiques : fuite inter-organisation, survente ou débit dupliqué restent des échecs bloquants.

Livrer un README reproductible, une décision d'architecture par défi, les résultats de tests, les métriques, un guide de reprise et les limites connues. Ce dossier devient un projet de portfolio montrant une démarche d'ingénierie, au-delà d'une interface qui fonctionne seulement en conditions idéales.
