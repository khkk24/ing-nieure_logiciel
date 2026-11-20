# 10 — Systèmes distribués : empêcher deux vérités de dépenser le même argent

## Objectifs et prérequis

Comprendre une partition réseau, distinguer réplication et consensus, puis comparer cohérence forte et droits préalloués. Prérequis : concurrence, idempotence, résilience et synchronisation. Durée indicative : 8 à 12 h.

## Deux copies de 1 000 ne représentent pas 2 000 disponibles

Une plateforme possède une copie du compte en Afrique et une autre en Europe. Le réseau entre les régions tombe. Chaque région lit 1 000 et reçoit une demande de retrait de 1 000. Si chacune prend une décision indépendante sur son solde répliqué, les deux opérations peuvent réussir avant que le conflit soit détecté.

Fusionner les historiques ensuite ne récupère pas automatiquement l'argent déjà remis. Il faut protéger le droit de dépenser **au moment de l'autorisation**.

**Invariant :** la somme des retraits autorisés sur les fonds initiaux ne dépasse pas les droits disponibles. Deux clés d'idempotence différentes restent deux opérations distinctes ; dédupliquer les requêtes ne suffit pas.

## La limite fondamentale

Lors d'une partition, un système ne peut pas garantir à la fois une cohérence linéarisable et la disponibilité de toutes les opérations sur les deux côtés. CAP n'est pas une règle marketing « choisir deux lettres en permanence » : la tension apparaît lorsqu'une partition empêche la coordination nécessaire.

Pour protéger un compte sans préallocation, on préfère souvent refuser ou différer le retrait du côté qui ne peut plus joindre l'autorité. Une lecture locale peut être affichée comme ancienne ; elle ne doit pas autoriser une dépense critique.

## POC A — Leader fixe et majorité

**Code :** [p10a_quorum.py](../pocs/p10a_quorum.py). **Ressources :** modèle séquentiel de trois membres AF, EU et W ; aucune connexion interrégionale.

```bash
python3 -m pocs.run 10a
```

AF est le leader fixe. Pendant la partition, AF et W forment une majorité et peuvent autoriser un retrait. EU, isolée, renvoie `UNAVAILABLE`. Après reconnexion, elle retrouve le solde consommé et refuse un second retrait. Une répétition de la première opération retrouve son résultat sans redébiter.

Ce modèle **n'implémente pas Raft** : il n'a ni élection, ni journaux répliqués, ni termes, ni persistance du consensus, ni panne du leader. Compter les réponses de deux serveurs n'est pas, à lui seul, un algorithme de consensus correct. Raft coordonne un journal répliqué avec des règles d'élection et d'engagement précises. [Article original](https://raft.github.io/raft.pdf).

**Extension réelle :** cluster de laboratoire d'une base à consensus, transaction conditionnelle sur le solde et identifiant de retrait unique. CockroachDB décrit l'utilisation de Raft dans sa couche de réplication. [Architecture de réplication](https://www.cockroachlabs.com/docs/stable/architecture/replication-layer). Tester séparation d'un nœud, perte du leader, réponse perdue après commit, guérison et comparaison des historiques.

Avec deux votants, la majorité exige les deux : une coupure bloque les écritures. Avec trois votants répartis 2+1 dans seulement deux régions, la région n'ayant qu'un votant reste dépendante de l'autre pour une majorité. Trois domaines de panne indépendants permettent une autre répartition, avec un coût de latence et d'exploitation. Le placement et les garanties de la base choisie doivent être vérifiés.

## POC B — Dépenser des droits préalloués

**Code :** [p10b_escrow.py](../pocs/p10b_escrow.py). **Ressources :** deux bases SQLite distinctes, contenant 600 et 400 unités de droits.

```bash
python3 -m pocs.run 10b
```

Avant la partition, les 1 000 unités sont réparties : 600 en Afrique, 400 en Europe. Pendant la coupure, aucune région ne peut autoriser seule 1 000. En revanche, 600 et 400 peuvent être consommés indépendamment sans dépasser le total. Chaque autorisation est locale, atomique et idempotente.

**Extension réelle :** quotas d'API par région, budgets de cartes prépayées ou inventaire réparti. Une transaction centrale alloue des droits ; chaque région consomme uniquement son budget durable. Les transferts de droits entre régions nécessitent leur propre protocole : réserver/retirer chez l'émetteur avant de rendre les droits utilisables chez le receveur, avec journal et déduplication. Le POC n'implémente pas leur réallocation.

Ce mécanisme améliore la disponibilité pour les opérations couvertes par les droits locaux. Il peut refuser une dépense alors que des fonds inutilisés existent ailleurs. Après perte d'une base régionale, restaurer un ancien budget sans rapprocher les dépenses pourrait recréer des droits : la durabilité locale reste essentielle.

## Choisir selon le produit

| Approche | Pendant la partition | Compromis |
|---|---|---|
| Autorité unique par compte | Côté non autorisé bloqué | Disponibilité régionale réduite |
| Base avec consensus | Seule une autorité correctement élue et capable de commit accepte | Coordination et latence |
| Droits préalloués | Consommation autonome jusqu'à la limite locale | Fonds fragmentés, réallocation complexe |
| Copies indépendantes avec fusion tardive | Les deux côtés écrivent librement | Inadapté au retrait sans découvert autorisé |

Un verrou distribué expirant n'est pas suffisant si un ancien propriétaire continue d'écrire : lorsque ce schéma est utilisé, l'autorité de stockage doit rejeter les anciens jetons de génération, ou **fencing tokens**. Ne pas fabriquer un consensus artisanal pour un système financier.

## Validation et livrable

Tester perte, duplication et retard des messages, partition asymétrique, leader isolé et retour d'un ancien nœud. Vérifier la somme des débits réellement acceptés, pas seulement les soldes affichés. Pour un vrai cluster, enregistrer l'historique d'invocation/réponse et analyser les propriétés promises ; les modèles locaux ne prouvent pas sa linéarisabilité.

Exercice : peut-on garantir deux retraits de 1 000 disponibles dans chaque région sur les mêmes 1 000, sans communication ni crédit ? **Non.** Livrable : règle d'autorité, choix de disponibilité, budget de droits éventuel et historique d'un test de partition.
