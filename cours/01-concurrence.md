# 01 — Concurrence : le dernier billet ne peut avoir qu'un acheteur

## Objectifs et prérequis

Comprendre une course critique, choisir entre une écriture conditionnelle, un verrou et une version, puis vérifier la garantie sous plusieurs connexions. Prérequis : [fondations](00-fondations.md), `SELECT`, `UPDATE`, transaction. Durée indicative : 6 à 8 h.

## Le problème dans sa globalité

Il reste un billet. Alice lit « 1 ». Bob lit « 1 ». Alice confirme sa vente. Bob confirme aussi la sienne. Chaque traitement semble correct pris isolément, mais leur combinaison vend deux fois la ressource.

Le problème apparaît également dans les quotas d'API, les créneaux médicaux, les places de parking et les éditions de devis. Le code `if disponible: réserver()` sépare la vérification de l'action. Entre les deux, le monde peut changer : c'est une course de type « vérifier puis agir ».

**Invariant billetterie :** ventes confirmées ≤ capacité et stock restant ≥ 0. **Invariant devis :** une écriture fondée sur une ancienne version ne doit pas effacer silencieusement une modification plus récente.

## Construire la solution

Pour un stock simple, faire vérifier la condition par la base au moment de l'écriture :

```sql
UPDATE stock SET quantity = quantity - 1
WHERE product_id = 42 AND quantity > 0
RETURNING quantity;
```

Une ligne retournée signifie succès ; aucune ligne signifie échec de la condition. L'insertion de la réservation doit appartenir à la **même transaction**. Si l'on décrémente puis que l'on crée la commande dans une transaction séparée, un autre problème apparaît, étudié aux défis 03 et 06.

Pour un devis, envoyer une version `v` avec la demande et utiliser `WHERE version = v`, en incrémentant la version. Si personne n'a modifié la ligne, l'écriture réussit. Sinon, renvoyer un conflit avec la version actuelle ; ne pas réessayer aveuglément une intention devenue obsolète.

Pour plusieurs lignes dépendantes, utiliser des verrous de lignes dans un ordre stable, ou l'isolation sérialisable avec reprise de la transaction entière lorsque la base signale un conflit. PostgreSQL expose des verrous explicites et les transactions peuvent aussi rencontrer des interblocages. [Documentation officielle des verrous](https://www.postgresql.org/docs/current/explicit-locking.html).

## POC A — Dernier ticket

**Code :** [p01a_ticket.py](../pocs/p01a_ticket.py). **Ressources :** Python, SQLite intégré, 24 threads et une base temporaire.

```bash
python3 -m pocs.run 01a
```

1. Observer le contre-exemple : deux instantanés du stock autorisent deux ventes naïves.
2. Examiner la barrière qui fait partir les acheteurs ensemble.
3. Chaque acheteur ouvre sa propre connexion et tente un `UPDATE` conditionnel.
4. Vérifier `ventes_atomiques = 1` et `stock_final = 0`.

**Extension réelle :** API de billetterie + PostgreSQL ; ajouter une table `reservations`, un identifiant d'achat et une expiration. Tester 100 demandes sur un stock de 10. Une expiration doit libérer une réservation une seule fois, sans libérer une vente déjà payée. L'[atelier PostgreSQL](../ateliers/postgresql/README.md) permet de tester la contention sur le moteur cible.

## POC B — Deux commerciaux modifient un devis

**Code :** [p01b_version.py](../pocs/p01b_version.py). **Ressources :** Python et SQLite.

```bash
python3 -m pocs.run 01b
```

Les deux commerciaux partent de la version 1. Le premier fixe 120 € et crée la version 2 ; le second propose 90 € avec la version 1. Le second est rejeté et le devis reste à 120 €.

**Extension réelle :** `GET /quotes/1` retourne un `ETag`, `PATCH` exige `If-Match`. Une précondition périmée produit `412`. L'interface affiche les différences et demande une nouvelle décision. Tester également un conflit sur un champ calculé.

## Choisir et mesurer

| Technique | Quand la choisir | Coût ou limite |
|---|---|---|
| Écriture conditionnelle | Stock ou quota simple | Point chaud si tous écrivent la même ligne |
| Version optimiste | Conflits peu fréquents, édition humaine | Il faut traiter le conflit côté produit |
| Verrou de ligne | Décision sur plusieurs valeurs | Attente, interblocages possibles |
| Sérialisable | Invariants traversant plusieurs lectures | Transactions parfois annulées et rejouées |

Un verrou Python ne couvre pas plusieurs serveurs. Redis peut aider certains usages de coordination ; il ne remplace pas automatiquement les contraintes de la base qui détient le stock. SQLite sérialise les écritures différemment de PostgreSQL : le POC démontre l'invariant, pas leurs performances respectives.

Mesurer taux de conflits, attente de verrou, durée de transaction, débit utile et stock négatif. Garder les transactions courtes, sans appel de paiement à l'intérieur.

## Vérification de compréhension

Pourquoi un UUID ne résout-il pas la survente ? **Il distingue les commandes, sans arbitrer le stock commun.** Quand faut-il réessayer ? **Pour un conflit technique rejouable ; pour un devis modifié humainement, réévaluer l'intention.**

Livrable : chronologie de la course, invariant, deux sorties de POC et justification du mécanisme choisi pour une prise de rendez-vous. Lecture complémentaire : [isolation PostgreSQL](https://www.postgresql.org/docs/16/transaction-iso.html).
