# Contribuer au parcours

Travailler sur une branche dédiée, en conservant les changements existants. Décrire le problème, l'invariant protégé et les limites du POC. Les cours sont en français ; les données financières et juridiques doivent rester fictives.

## Vérifier avant publication

```bash
python3 -m unittest discover -s tests -v
python3 -m scripts.check_docs
python3 -m scripts.build_wiki
python3 -m compileall -q pocs tests scripts ateliers/postgresql
```

Ajouter un test adverse lorsqu'un mécanisme change. Éviter les dépendances inutiles : les expériences locales utilisent la bibliothèque standard Python.

## Mettre à jour un cours

Modifier le fichier d'origine dans `cours/` ou `ressources/`. Le wiki est généré : son organisation et sa procédure de publication sont décrites dans [Maintenance](docs/wiki/Maintenance.md). Ne pas présenter un atelier préparé comme exécuté ; indiquer le système et les commandes de validation.

Ne placer aucun secret dans le dépôt. Le mot de passe de l'atelier Docker est une valeur publique de démonstration, uniquement destinée au conteneur de laboratoire sans port publié.
