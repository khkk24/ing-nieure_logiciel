# 08 — Synchronisation : deux appareils, plusieurs intentions à préserver

## Objectifs et prérequis

Détecter une modification concurrente hors ligne, choisir une fusion adaptée et comprendre les garanties d'un CRDT. Prérequis : versions optimistes, idempotence et collections. Durée indicative : 8 à 10 h.

## Le serveur ne peut pas deviner l'intention

Deux téléphones téléchargent la même fiche. Sans réseau, A modifie le titre et B modifie la ville. Remplacer intégralement la fiche à chaque synchronisation fait perdre une modification. Si les deux changent le titre, les deux valeurs peuvent être légitimes ; décider « dernier arrivé gagne » cache un choix métier.

L'heure des appareils n'est pas une autorité fiable : horloges décalées, modification des réglages et synchronisation tardive empêchent d'assimiler timestamp et causalité. Un compteur local seul ne compare pas non plus les événements de deux appareils indépendants.

**Invariant :** aucune modification concurrente significative ne disparaît sans une politique explicite. La convergence signifie que les réplicas finissent avec le même état après réception des mêmes changements ; elle ne garantit pas que cet état respecte toutes les contraintes métier.

## POC A — Fusion à trois versions

**Code :** [p08a_merge.py](../pocs/p08a_merge.py). **Ressources :** trois dictionnaires, schéma fixe, pas de serveur.

```bash
python3 -m pocs.run 08a
```

Conserver la version de base téléchargée, la version locale et la version distante. Pour chaque champ : si une seule branche l'a modifié, conserver cette modification ; si les deux ont produit la même valeur, la conserver ; si elles ont produit deux valeurs différentes, conserver un conflit explicite.

Le premier scénario fusionne titre et ville. Le second laisse le titre non résolu et garde base, valeur A et valeur B. Résultat : aucune préférence silencieuse pour l'un des appareils.

**Extension réelle :** fiches d'inspection sur mobile, stockage local SQLite ou IndexedDB, queue d'opérations avec identifiants stables, API de synchronisation avec version de base, journal des conflits et écran de résolution. Le serveur applique la résolution avec une précondition de version pour éviter un troisième écrasement concurrent.

Le POC ne gère pas les suppressions de champs : une suppression réelle doit devenir une opération ou une marque explicite, sinon elle se confond avec une donnée absente. Prévoir aussi révocation d'accès pendant le hors-ligne, migration de schéma et suppression d'un compte.

## POC B — Liste partagée en CRDT

**Code :** [p08b_crdt.py](../pocs/p08b_crdt.py). **Ressources :** ensemble observed-remove, identifiants d'ajout uniques.

```bash
python3 -m pocs.run 08b
```

La liste initiale contient « lait ». A supprime l'ajout qu'il connaît et ajoute « pain ». B, hors ligne, ajoute à nouveau « lait » avec un nouvel identifiant. La fusion combine les ajouts et les marques de suppression. A n'avait pas observé l'ajout de B : celui-ci survit, selon la sémantique **add-wins**.

Vérifier que fusionner A avec B ou B avec A donne le même résultat, et que rejouer une fusion ne crée pas de doublon. L'identifiant de chaque ajout doit être unique sur tous les appareils, même après réinstallation ; les tags fixes du POC servent uniquement à rendre l'expérience reproductible.

**Extension réelle :** liste collaborative ou éditeur de notes avec Yjs, persistance locale et relais de synchronisation authentifié. Yjs fournit des types partagés et des mécanismes de fusion pour des applications collaboratives. [Documentation Yjs](https://docs.yjs.dev/). Pour du texte riche, utiliser un CRDT éprouvé plutôt que transposer naïvement cet ensemble à des chaînes de caractères.

## Choisir une politique par donnée

| Donnée | Politique possible | Conséquence |
|---|---|---|
| Préférence visuelle mineure | Dernière version selon ordre défini | Une intention peut être écrasée |
| Fiche métier | Fusion par champ + conflit explicite | Interface de résolution nécessaire |
| Texte collaboratif | CRDT adapté aux séquences | Métadonnées et sémantique à comprendre |
| Solde ou stock rare | Autorité forte ou droits préalloués | Pas de liberté d'écriture globale hors ligne |

Les propriétés mathématiques recherchées pour une fusion d'état sont commutativité, associativité et idempotence. Elles permettent de tolérer ordre variable et répétition sous les hypothèses du type choisi. Elles ne rendent pas toute règle métier automatiquement distribuable. [Synthèse de recherche sur les CRDT](https://arxiv.org/abs/1806.10254).

Les tombstones, ou marques de suppression, peuvent croître. Leur nettoyage exige de connaître les réplicas susceptibles de revenir avec un vieil état ; un simple TTL peut ressusciter des données supprimées.

## Validation et livrable

Tester les permutations d'ordre de messages, duplications, longue déconnexion, ajout/suppression concurrente et arrivée d'un troisième appareil. Mesurer taille du journal, durée de convergence et nombre de conflits humains.

Exercice : peut-on stocker un solde bancaire dans un compteur CRDT et autoriser chaque téléphone à retirer librement ? **La convergence du total n'empêche pas un découvert au moment des décisions.** Voir le défi 10.

Livrable : choix de fusion par champ, preuves de convergence, capture d'un conflit préservé et protocole de reprise avec contrôle d'accès.
