# Passer des POC locaux à l'infrastructure réelle

Les vingt POC sont autonomes. Ces ateliers supplémentaires utilisent de vrais outils et servent de pont vers les extensions décrites dans les cours.

| Atelier | Ce qu'il permet de vérifier | Prérequis |
|---|---|---|
| [PostgreSQL](postgresql/README.md) | Dernier ticket sous concurrence entre connexions PostgreSQL | Docker avec Compose, Python |
| [Kubernetes](kubernetes/README.md) | Rollout réel, sondes et trafic pendant remplacement | Cluster local existant, kubectl |

**Statut : fichiers préparés, non exécutés dans l'environnement de création.** Ne pas confondre les tests Python locaux réussis avec une validation de ces ateliers. Les commandes visent exclusivement les ressources de laboratoire nommées ici.

Budget matériel indicatif : les POC demandent peu de ressources ; prévoir quelques Go de mémoire disponibles pour Docker, et davantage pour un cluster local. La consommation dépend de la distribution Kubernetes et du matériel. Aucun fournisseur cloud n'est requis.

Pour les autres technologies, les cours donnent un contrat de POC réel : architecture, panne à injecter, critères et limites. Les intégrations broker, Temporal, Yjs, base à consensus et fournisseur LLM sont des extensions guidées à réaliser ; elles ne sont pas déjà déployées dans ce dépôt.
