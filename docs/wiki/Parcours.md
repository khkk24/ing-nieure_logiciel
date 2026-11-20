# Parcours conseillé

Le parcours est organisé par dépendances : comprendre les invariants avant d'ajouter les systèmes distribués ou l'IA.

| Étape | Cours | POC | Compétence à démontrer |
|---|---|---|---|
| 0 | [Fondations](../../cours/00-fondations.md) | Lecture préparatoire | Expliquer invariant, transaction et résultat inconnu |
| 1 | [Concurrence](../../cours/01-concurrence.md) | 01a, 01b | Protéger une ressource rare et détecter une version périmée |
| 2 | [Idempotence](../../cours/02-idempotence.md) | 02a, 02b | Rejouer une demande sans répéter l'effet |
| 3 | [Résilience](../../cours/03-resilience.md) | 03a, 03b | Récupérer après crash et contenir une dépendance défaillante |
| 4 | [Sécurité](../../cours/05-securite.md) | 05a, 05b | Tester les droits sur chaque ressource et organisation |
| 5 | [Fiabilité métier](../../cours/06-fiabilite.md) | 06a, 06b | Reprendre un processus et ses compensations |
| 6 | [Scalabilité](../../cours/04-scalabilite.md) | 04a, 04b | Borner la charge et maîtriser les ressources |
| 7 | [Déploiement](../../cours/07-deploiement.md) | 07a, 07b | Faire coexister deux versions et migrer le schéma |
| 8 | [Synchronisation](../../cours/08-synchronisation.md) | 08a, 08b | Préserver les intentions des appareils hors ligne |
| 9 | [Systèmes distribués](../../cours/10-systemes-distribues.md) | 10a, 10b | Choisir une autorité pendant une partition |
| 10 | [Fiabilité de l'IA](../../cours/09-fiabilite-ia.md) | 09a, 09b | Contrôler les preuves et s'abstenir |

## Routine pour chaque étape

1. Lire la situation métier et dessiner une exécution qui échoue.
2. Écrire la propriété que la solution doit préserver.
3. Exécuter les deux POC et expliquer les observations.
4. Ajouter un cas adverse ou retirer une protection dans une copie de travail.
5. Comparer au moins deux architectures et noter leurs limites.
6. Compléter [le compte rendu](../../ressources/compte-rendu.md).

Prévoir une étape par semaine à temps partiel, en adaptant le rythme au niveau. Les extensions d'infrastructure nécessitent plus de temps que les scripts locaux. Les durées détaillées sont indiquées dans chaque cours.

## Trois niveaux de maîtrise

**Comprendre :** expliquer la panne sans nom de produit. **Démontrer :** la reproduire et vérifier la solution. **Transposer :** implémenter l'extension dans une API réelle avec métriques et reprise.

Ne passer à l'étape suivante qu'après avoir expliqué les limites du POC précédent. Terminer avec [le projet final](../../ressources/projet-final.md), qui assemble les garanties dans un produit cohérent.
