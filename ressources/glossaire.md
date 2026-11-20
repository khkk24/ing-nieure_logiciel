# Glossaire pratique

| Terme | Explication |
|---|---|
| Invariant | Règle qui doit rester vraie pour toutes les exécutions couvertes |
| POC | Expérience limitée vérifiant la faisabilité d'une idée |
| Atomicité | Toutes les modifications d'une transaction ou aucune |
| Isolation | Règles de visibilité et d'interaction des transactions concurrentes |
| Durabilité | Persistance des commits selon les pannes couvertes par le stockage |
| Concurrence | Plusieurs opérations dont les périodes d'exécution se chevauchent |
| Course critique | Résultat incorrect dépendant de l'ordre d'exécution |
| Compare-and-swap | Écrire seulement si une valeur ou version attendue est encore actuelle |
| Idempotence | Rejouer une même intention sans nouvel effet métier |
| ACK | Accusé de réception ou de traitement, dont la portée doit être précisée |
| Timeout | Délai d'attente dépassé ; résultat potentiellement inconnu |
| Retry | Nouvelle tentative, adaptée aux seules erreurs rejouables |
| Backoff / jitter | Attente croissante et aléatoire pour espacer les reprises |
| Circuit breaker | Suspension temporaire des appels vers une dépendance en échec |
| Bulkhead | Compartiment de capacité empêchant une panne d'épuiser toutes les ressources |
| RPO / RTO | Perte de données tolérée / délai de rétablissement visé |
| Outbox / inbox | Intentions de publication / identifiants consommés, persistés avec l'effet local |
| Saga | Enchaînement métier récupérable avec compensations possibles |
| Compensation | Nouvelle opération qui corrige un effet, sans effacer son historique |
| Backpressure | Faire ralentir ou refuser l'entrée quand l'aval n'absorbe plus la charge |
| Single-flight | Partager un même calcul en cours entre plusieurs demandeurs |
| p95 / p99 | Latence en dessous de laquelle se trouvent 95 % / 99 % des observations |
| SLI / SLO | Indicateur de service / objectif défini sur cet indicateur |
| BOLA / IDOR | Accès indu à un objet par manipulation d'identifiant |
| RBAC / ABAC | Autorisation par rôles / par attributs et contexte |
| Tenant | Organisation ou espace de clients à isoler dans un service partagé |
| Readiness / liveness | Aptitude à recevoir du trafic / nécessité de redémarrer un processus |
| Expand/contract | Étendre un schéma, migrer progressivement, retirer l'ancienne structure |
| CRDT | Type de données conçu pour une convergence déterministe sous ses hypothèses |
| Tombstone | Marque durable indiquant une suppression |
| Causalité | Relation « cet événement a pu connaître celui-ci » |
| RAG | Recherche de documents utilisée pour alimenter une génération de texte |
| Embedding | Représentation numérique utilisée notamment pour la similarité |
| Hallucination | Contenu généré incorrect ou non étayé présenté comme factuel |
| Abstention | Refus explicite de conclure faute de preuves suffisantes |
| Partition réseau | Interruption de communication entre certaines parties d'un système |
| Linéarisabilité | Opérations observables comme si elles avaient lieu instantanément dans un ordre compatible avec le temps réel |
| Consensus | Accord entre participants selon un protocole et un modèle de panne définis |
| Quorum | Ensemble de participants requis pour une décision selon le protocole |
| Fencing token | Génération monotone que la ressource vérifie pour rejeter un ancien propriétaire |
| Escrow | Droits d'opération préalloués permettant une autonomie locale bornée |
