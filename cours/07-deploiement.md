# 07 — Déploiement : changer le logiciel pendant qu'il sert

## Objectifs et prérequis

Séparer disponibilité du processus et aptitude à servir, assurer la coexistence de versions et rendre les migrations progressives. Prérequis : API, résilience et bases SQL. Durée indicative : 8 à 10 h.

## « Le conteneur démarre » ne veut pas dire « le service est prêt »

Pendant une mise à jour, l'ancienne version peut terminer une requête alors que la nouvelle initialise son cache ou ses connexions. Arrêter toutes les anciennes instances avant que les nouvelles soient prêtes crée une coupure. Même avec deux instances actives, un changement incompatible de schéma peut casser l'une d'elles.

**Invariant de routage :** sous les hypothèses de capacité et de santé du déploiement, toute nouvelle requête dispose d'une instance prête. **Invariant de compatibilité :** les versions coexistant pendant la transition comprennent les données qu'elles lisent et écrivent.

Aucune stratégie ne promet une absence absolue d'incident : mauvaises sondes, ressources insuffisantes, clients sans reprise et pannes simultanées doivent être évalués.

## Construire une mise à jour progressive

Une sonde de **readiness** décide si l'instance reçoit le trafic. La **liveness** décide si elle doit être redémarrée ; tester systématiquement une dépendance partagée dans cette sonde peut provoquer une tempête de redémarrages. Une sonde de démarrage protège les initialisations longues.

Créer une nouvelle instance, attendre qu'elle soit prête, retirer une ancienne du routage, terminer ses requêtes et seulement ensuite l'arrêter. Le drainage doit aussi tenir compte de la propagation du retrait et des connexions persistantes. Les tâches longues doivent être déportées ou reprises selon un protocole durable.

Kubernetes expose des mises à jour progressives et les paramètres `maxUnavailable` et `maxSurge`. Leur utilité dépend de sondes correctes et d'une capacité disponible pour les instances supplémentaires. [Tutoriel officiel](https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/).

## POC A — Readiness, drainage et retour arrière

**Code :** [p07a_rollout.py](../pocs/p07a_rollout.py). **Ressources :** modèle de routeur et d'instances en Python.

```bash
python3 -m pocs.run 07a
```

La version v1 sert pendant que v2 n'est pas prête. v2 devient prête avant le drainage de v1. La requête déjà engagée sur v1 termine. Une défaillance de v2 provoque ensuite un routage vers une instance v1 disponible. Résultat : séquence `v1, v2, v2, v1` sans absence d'instance dans les étapes modélisées.

**Extension réelle :** exécuter le [laboratoire Kubernetes](../ateliers/kubernetes/README.md), lancer des requêtes pendant le rollout, observer les codes et latences, puis rendre la nouvelle image volontairement indisponible. Pour une véritable API, implémenter SIGTERM, arrêt de l'admission et fin des requêtes en cours. Le POC ne vérifie pas ces mécanismes réseau réels.

## POC B — Renommer un champ sans casser l'ancienne version

**Code :** [p07b_migration.py](../pocs/p07b_migration.py). **Ressources :** SQLite avec support `DROP COLUMN`, inclus dans les versions récentes compatibles.

```bash
python3 -m pocs.run 07b
```

Le champ `name` devient `display_name` en plusieurs phases :

1. **Expand :** ajouter la colonne, garder l'ancienne.
2. Installer un mécanisme de synchronisation des anciennes écritures. Ici, des triggers assurent cette compatibilité.
3. La nouvelle lecture utilise temporairement `COALESCE(display_name, name)`.
4. Remplir les anciennes lignes par lots ; le POC ne possède qu'une ligne.
5. La nouvelle version écrit les deux champs pendant la coexistence.
6. Après retrait des anciens writers et fin de leur fenêtre de rollback, **contract** supprime l'ancienne colonne et les triggers.

Résultat : écriture v1 visible de v2, écriture v2 visible de v1, puis valeur préservée après contraction.

**Extension réelle :** PostgreSQL avec une table volumineuse, mesure des verrous et backfill reprenable par tranches. Tester explicitement v1 et v2 sur le schéma intermédiaire. Ne pas supprimer une colonne tant qu'un job ancien, un rapport ou un consommateur peut l'utiliser.

## Choisir la stratégie

| Stratégie | Avantage | Condition |
|---|---|---|
| Rolling update | Capacité supplémentaire modérée | Versions compatibles |
| Blue/green | Bascule rapide entre deux ensembles | Capacité doublée et données compatibles |
| Canary | Exposer d'abord une fraction du trafic | Métriques et critère d'arrêt fiables |

Un rollback applicatif ne restaure pas automatiquement des données transformées de façon destructive. Prévoir une marche avant corrective et des sauvegardes restaurables. Un PodDisruptionBudget ne remplace pas les paramètres de rollout et ne protège pas contre toutes les pannes.

## Validation et livrable

Définir avant livraison les critères : erreurs, latence p99, saturation, métriques métier, durée de transition. Contrôler les résultats pendant le trafic, pas uniquement `kubectl rollout status`. Les essais locaux ne représentent pas toutes les conditions d'un réseau de production.

Exercice : peut-on supprimer `name` dès que v2 a démarré ? **Non : v1 et les anciens traitements peuvent encore l'utiliser.** Livrable : chronologie de déploiement, matrice de compatibilité, mesure pendant le rollout et procédure de retour arrière réaliste.
