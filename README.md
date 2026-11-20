# Dix défis pour construire des applications fiables et modernes

[![CI](https://github.com/khkk24/ing-nieure_logiciel/actions/workflows/ci.yml/badge.svg)](https://github.com/khkk24/ing-nieure_logiciel/actions/workflows/ci.yml)

**[Wiki organisé](https://github.com/khkk24/ing-nieure_logiciel/wiki) · [Parcours conseillé](docs/wiki/Parcours.md) · [Les 20 POC](docs/wiki/Index-POC.md)**

Un parcours pratique en français : **10 cours, 20 POC exécutables, des ateliers PostgreSQL et Kubernetes**. L'objectif est de savoir expliquer une panne, choisir une garantie adaptée et démontrer cette garantie par une expérience reproductible.

Les exemples forment trois projets fil rouge : **une billetterie et sa boutique**, **une application de terrain utilisable hors ligne**, **un assistant documentaire à références vérifiées**. Les virements servent à étudier les invariants ; les données financières et juridiques sont fictives.

## Commencer en cinq minutes

Prérequis : Python **3.11 ou ultérieur**, un terminal et les bases de programmation. Aucun paquet externe, compte cloud, secret ou paiement n'est requis pour les 20 POC. Les tests ont été exécutés avec Python 3.14.7 ; les autres versions compatibles n'ont pas été exécutées ici.

Depuis la racine de ce dossier :

```bash
python3 -m pocs.run --list
python3 -m pocs.run 01a
python3 -m pocs.run 01b
python3 -m unittest discover -s tests -v
```

Lire d'abord [les fondations](cours/00-fondations.md), puis [le cours sur la concurrence](cours/01-concurrence.md). Les scripts créent leurs bases dans des dossiers temporaires, nettoyés à la fin. Les résultats sont imprimés en JSON ; toute garantie violée provoque un échec du programme.

## Les dix défis et leurs deux expériences

| Défi | Question centrale | POC A | POC B |
|---|---|---|---|
| [01 — Concurrence](cours/01-concurrence.md) | Qui peut modifier une ressource simultanément ? | `01a` : dernier ticket, 24 acheteurs | `01b` : devis et version optimiste |
| [02 — Idempotence](cours/02-idempotence.md) | Que se passe-t-il si une demande revient ? | `02a` : débit local et réponse perdue | `02b` : événement livré plusieurs fois |
| [03 — Résilience](cours/03-resilience.md) | Comment survivre à une panne ? | `03a` : crash réel d'un processus de virement | `03b` : circuit breaker et reprise |
| [04 — Scalabilité](cours/04-scalabilite.md) | Comment absorber la charge à coût maîtrisé ? | `04a` : cache et calcul partagé | `04b` : admission bornée et file durable |
| [05 — Sécurité](cours/05-securite.md) | Qui a le droit de faire quoi sur quelle donnée ? | `05a` : factures privées et ID manipulé | `05b` : isolation des organisations |
| [06 — Fiabilité métier](cours/06-fiabilite.md) | Comment coordonner plusieurs services ? | `06a` : outbox et inbox | `06b` : saga et compensation durable |
| [07 — Déploiement](cours/07-deploiement.md) | Comment faire évoluer un service actif ? | `07a` : readiness, drainage, rollback | `07b` : migration expand/contract |
| [08 — Synchronisation](cours/08-synchronisation.md) | Comment réunir des modifications hors ligne ? | `08a` : fusion à trois versions | `08b` : ensemble CRDT add-wins |
| [09 — Fiabilité de l'IA](cours/09-fiabilite-ia.md) | Comment vérifier les preuves et savoir s'abstenir ? | `09a` : références, citations, dates | `09b` : contrôle des affirmations et évaluation |
| [10 — Systèmes distribués](cours/10-systemes-distribues.md) | Quelle vérité accepter pendant une partition ? | `10a` : leader et majorité | `10b` : budgets régionaux préalloués |

## Ce que les POC démontrent

**POC** signifie preuve de concept : une expérience limitée, avec une hypothèse explicite et un résultat observable. Ici, les opérations SQLite utilisent une vraie base locale ; les POC 01a, 02a et 04a lancent des threads ; le POC 03a arrête brutalement un sous-processus. Les services de paiement et de stock du POC 06b utilisent trois bases indépendantes mais des appels locaux.

Le routage Kubernetes, le disjoncteur et le quorum sont des **modèles déterministes**, pas des essais réseau. Le POC IA utilise un corpus fictif et des sorties de modèle simulées. Le cache ne couvre qu'un processus. Ces limites figurent dans chaque cours. Les POC n'attestent ni une capacité de deux millions d'utilisateurs, ni une disponibilité sans interruption, ni une fiabilité juridique générale.

Les [ateliers d'infrastructure](ateliers/README.md) permettent de passer à une vraie base PostgreSQL et à un cluster Kubernetes local. Ils demandent des outils supplémentaires ; ils n'ont pas été exécutés dans cet environnement, où Docker et kubectl ne sont pas disponibles.

## Méthode de travail

Pour chaque cours :

1. Dessiner la chronologie d'une panne avant de lire la solution.
2. Écrire l'invariant : une phrase qui doit rester vraie après toute exécution.
3. Exécuter les deux POC et expliquer chaque résultat.
4. Modifier un paramètre ou retirer une protection dans une copie du fichier pour provoquer un échec.
5. Réaliser l'extension vers un service réel décrite dans le cours.
6. Noter mesures, limites et décision d'architecture dans [le modèle de compte rendu](ressources/compte-rendu.md).

Progression conseillée : **00 → 01 → 02 → 03 → 05 → 06 → 04 → 07 → 08 → 10 → 09**. Le classement du tableau conserve les dix sujets initiaux ; cet ordre d'étude introduit les dépendances progressivement.

Prévoir environ **6 à 10 heures par défi**, davantage au début si SQL et HTTP sont nouveaux. Cette estimation concerne la lecture, les POC et une extension ; une plateforme complète en production demande un travail supplémentaire.

## Ressources et état du travail

- [Choisir une architecture, des serveurs et des bases](ressources/architecture.md)
- [Glossaire](ressources/glossaire.md)
- [Sources officielles et lectures](ressources/sources.md), consultées le 18 novembre 2026
- [Projet final et critères d'acceptation](ressources/projet-final.md)
- [Validation exécutée et limites](ressources/validation.md)

## GitHub Actions et wiki

La CI exécute les tests Python sur 3.11 à 3.14, vérifie les liens, génère les pages du wiki et teste la concurrence sur PostgreSQL. Consulter les [exécutions GitHub Actions](https://github.com/khkk24/ing-nieure_logiciel/actions) pour connaître le résultat du commit concerné. L'artefact `wiki-markdown` contient les pages générées ; sa création ne publie pas automatiquement le wiki.

Les cours sont la source de référence. Voir [la maintenance du wiki](docs/wiki/Maintenance.md) et [les règles de contribution](CONTRIBUTING.md). Aucun déploiement de production n'est effectué par la CI.
