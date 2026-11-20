# Entretenir les cours, GitHub Actions et le wiki

## Source unique

Modifier les cours dans `cours/`, les ressources dans `ressources/` et les pages d'accueil dans `docs/wiki/`. Ne pas corriger directement une page générée sur GitHub : elle serait remplacée lors de la prochaine publication.

```bash
python3 -m unittest discover -s tests -v
python3 -m scripts.check_docs
python3 -m scripts.build_wiki
```

Le dossier `build/wiki/` contient les pages prêtes pour le dépôt Git du wiki, avec leurs liens réécrits, un sommaire latéral, un pied de page et une navigation entre les cours. Il est ignoré par Git.

## Intégration continue

Le [workflow CI](../../.github/workflows/ci.yml) s'exécute à chaque push, pull request ou déclenchement manuel :

- Tests Python sur 3.11, 3.12, 3.13 et 3.14.
- Vérification des liens documentaires et génération du wiki.
- Archivage des pages dans l'artefact `wiki-markdown`.
- Test de concurrence sur PostgreSQL avec Docker Compose.

L'atelier Kubernetes n'est pas exécuté par ce workflow. La génération réussie d'un artefact ne signifie pas que le wiki en ligne a été mis à jour.

## Publier le wiki

Prérequis : une première page Wiki créée dans l'interface GitHub, Git et une authentification existante disposant des droits d'écriture. Le script utilise les identifiants Git configurés ; avec GitHub CLI, passer `--use-gh` après connexion au compte approprié.

```bash
python3 -m scripts.publish_wiki --use-gh
```

Le script reconstruit les pages, clone le wiki, met à jour uniquement les pages générées, puis crée un commit et pousse sans forcer. Il garde les autres pages existantes. Il utilise un dossier temporaire, sans toucher aux fichiers de travail. Le message contient le commit du projet utilisé pour générer le wiki.

Si un accès est refusé ou une modification distante arrive entre-temps, le push échoue : traiter la cause puis relancer. Le script ne crée pas de jeton, ne stocke pas de secret dans le dépôt et ne contourne pas les protections GitHub.

La publication du wiki est volontairement séparée des tests : elle exige des droits sur son dépôt Git. Aucun secret personnel n'est requis pour la CI de validation.

Référence : [gestion des pages et du dépôt Git du wiki](https://docs.github.com/en/communities/documenting-your-project-with-wikis/adding-or-editing-wiki-pages).
