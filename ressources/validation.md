# Validation du parcours

## Validation locale initiale — 18 novembre 2026

Environnement de création : macOS, Python 3.14.7. Le dépôt était vide, sur une branche `main` sans commit. Les nouveaux fichiers ont été créés sur **`codex/parcours-10-defis`**, sans commit ni push.

## Commandes et résultats

| Commande | Résultat |
|---|---|
| `python3 -m pocs.run --all` | Les 20 scénarios se terminent avec leurs invariants respectés |
| `python3 -m unittest discover -s tests -v` | 33 tests métier réussis lors de la validation initiale |
| `python3 -m unittest discover -s tests -p test_pocs.py -k 'model' -v` | 2 tests ciblés réussis après renforcement du contrôle des sorties IA malformées |
| `python3 -m compileall -q pocs tests ateliers/postgresql` | Compilation des sources Python réussie |

Un contrôle local des liens Markdown et des fichiers attendus a également été effectué. Aucun linter ou outil de typage n'était configuré dans ce dépôt initialement vide. Les tests n'ont aucune dépendance externe.

## Ce qui a réellement été exercé

- Vraies connexions SQLite et écritures concurrentes dans plusieurs threads.
- Arrêt brutal d'un sous-processus avant/après commit, puis relecture depuis une autre connexion.
- Reprises après exceptions simulant une perte de réponse ou une compensation indisponible.
- Politique d'accès, fusion et contrôle documentaire sur des entrées adverses.
- Ordres de fusion de trois réplicas et limites de budget sous accès concurrents.

## Ce qui n'a pas été exécuté

- Docker Compose et PostgreSQL : Docker absent de l'environnement.
- Kubernetes : kubectl absent et aucun cluster local utilisé.
- Vrais paiements, fournisseurs LLM, broker, Temporal, Yjs ou cluster de consensus.
- Tests de charge représentatifs de millions d'utilisateurs, partitions réseau réelles, panne de disque ou panne électrique.

Les POC 03b, 07a et 10a sont des modèles déterministes ; les POC IA utilisent des sorties simulées et un corpus fictif. Les validations locales ne certifient pas les propriétés d'une infrastructure de production.

## Fichiers livrés

- `README.md` : entrée du parcours et commandes.
- `cours/` : introduction et dix cours avec deux expériences chacun.
- `pocs/` : vingt expériences, utilitaires et lanceur.
- `tests/` : scénarios et tests adverses.
- `ateliers/` : prolongements PostgreSQL et Kubernetes, explicitement non exécutés.
- `ressources/` : architecture, glossaire, sources, projet final, compte rendu et validation.
- `.gitignore` : caches Python et fichiers locaux exclus.

## Préparation GitHub — 20 novembre 2026

- 39 tests locaux réussis : 33 tests métier et 6 tests du générateur de wiki.
- `python3 -m scripts.check_docs` : 26 sources Markdown et 26 fichiers de wiki vérifiés.
- `python3 -m scripts.build_wiki` : génération reproductible des 24 pages de contenu, du menu et du pied de page.
- `python3 -m compileall -q pocs tests scripts ateliers/postgresql` : compilation réussie.
- Workflow ajouté : tests Python 3.11–3.14, documentation et PostgreSQL. Consulter [GitHub Actions](https://github.com/khkk24/ing-nieure_logiciel/actions) pour l’état distant de chaque commit.

Les pages de navigation se trouvent dans `docs/wiki/`, les outils dans `scripts/`, et les règles de contribution dans `CONTRIBUTING.md`. La publication du wiki est séparée de sa génération en CI.
