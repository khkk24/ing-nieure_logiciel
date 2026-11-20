# Ingénierie logicielle — dix défis, vingt expériences

Bienvenue dans le parcours **ing-nieure_logiciel** : apprendre à construire des applications qui restent correctes face aux accès concurrents, aux pannes, à la charge et aux réponses incertaines d'une IA.

**Commencer : [itinéraire conseillé](Parcours.md) → [les fondations](../../cours/00-fondations.md) → [le dernier billet](../../cours/01-concurrence.md).**

## Trois projets fil rouge

| Projet | Ce que tu apprendras |
|---|---|
| Billetterie et boutique | Concurrence, idempotence, transactions, sagas, montée en charge |
| Application de terrain | Autorisations, synchronisation hors ligne, conflits, déploiements |
| Assistant documentaire | Sources vérifiées, preuves par affirmation, abstention, évaluation |

## Explorer le wiki

- [Parcours progressif et exercices](Parcours.md)
- [Catalogue des 20 POC et commandes](Index-POC.md)
- [Architecture : serveurs, bases et outils](../../ressources/architecture.md)
- [Ateliers PostgreSQL et Kubernetes](../../ateliers/README.md)
- [Projet final et critères de réussite](../../ressources/projet-final.md)
- [Glossaire](../../ressources/glossaire.md), [sources officielles](../../ressources/sources.md) et [validation](../../ressources/validation.md)

## Première expérience

Installer Python 3.11 ou ultérieur, récupérer le dépôt puis lancer :

```bash
git clone https://github.com/khkk24/ing-nieure_logiciel.git
cd ing-nieure_logiciel
python3 -m pocs.run 01a
python3 -m unittest discover -s tests -v
```

Aucune dépendance externe pour les POC. Le premier résultat doit montrer une seule vente pour 24 acheteurs concurrents. Chaque cours explique le résultat, les limites et l'extension vers une infrastructure réelle.

## Bien lire les résultats

Un POC local valide un mécanisme dans un périmètre précis. Certaines expériences sont des modèles déterministes ; l'assistant juridique emploie des données fictives. Consulter les limites du cours et les résultats de CI avant de conclure qu'une architecture est prête pour la production.

Les fichiers des cours sont la référence. Les pages sont générées à partir de ceux-ci : [entretenir le wiki](Maintenance.md).
