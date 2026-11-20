# 04 — Scalabilité : absorber la charge en protégeant les ressources

## Objectifs et prérequis

Transformer un nombre d'utilisateurs en charge mesurable, identifier un goulot, borner la file d'attente et comparer coût et débit utile. Prérequis : API, transactions, résilience. Durée indicative : 8 à 10 h.

## Deux millions d'utilisateurs ne sont pas une unité de charge

Il faut distinguer inscrits, actifs par jour, simultanés et requêtes par seconde. Exemple **hypothétique** : 2 millions d'inscrits, 5 % actifs dans une fenêtre de dix minutes, chacun envoyant six requêtes : 600 000 / 600 = **1 000 requêtes/s en moyenne**. Un pic peut être beaucoup plus élevé. La répartition lectures/écritures et le coût de chaque opération changent tout.

À débit stable, la loi de Little relie travail en cours, débit et temps moyen : `L = λ × W`. À 1 000 requêtes/s et 0,2 s en moyenne, environ 200 requêtes sont en cours. Si une dépendance ralentit à 2 s, on passe à environ 2 000, avant même une hausse de trafic.

**Invariants :** une demande acquittée comme durable est retrouvable ; le travail en attente reste borné ; les opérations critiques restent correctes sous charge. Refuser explicitement une nouvelle demande n'est pas perdre silencieusement une demande déjà acceptée.

## Une progression raisonnable

Mesurer d'abord les requêtes SQL, index, temps CPU, attentes d'entrée/sortie et pools. Éliminer les lectures inutiles et paginer. Servir les contenus statiques par un CDN. Ajouter un cache aux lectures dont la fraîcheur peut être relâchée. Séparer les traitements longs dans une file durable. Répartir ensuite l'API sans état local indispensable sur plusieurs instances.

Ajouter des serveurs applicatifs peut saturer encore plus la base. Le budget de connexions doit être global : 50 instances × 20 connexions représentent 1 000 connexions potentielles. Un pooler aide à les maîtriser ; il ne rend pas une requête coûteuse gratuite.

## POC A — Éviter le cache stampede

**Code :** [p04a_cache.py](../pocs/p04a_cache.py). **Ressources :** 32 threads, cache local à une clé, horloge contrôlée.

```bash
python3 -m pocs.run 04a
```

Les requêtes arrivent au même moment sur une valeur absente. Un mécanisme single-flight partage le recalcul : une seule lecture simulée de la base fournit les 32 réponses. Après expiration, une nouvelle lecture produit la version suivante.

**Extension réelle :** catalogue HTTP, PostgreSQL, cache partagé facultatif et test de charge. Mesurer hit ratio, p95/p99 et nombre de requêtes SQL. Tester l'expiration simultanée de nombreuses clés, puis TTL légèrement aléatoires, recalcul groupé par clé et service éventuel d'une valeur périmée autorisée.

Le cache du POC tient dans un processus et son verrou global ne convient pas à un catalogue complet. Ne jamais décider un débit ou une réservation sur un stock seulement lu dans un cache. La base reste l'autorité d'écriture.

## POC B — Accepter durablement ou refuser clairement

**Code :** [p04b_queue.py](../pocs/p04b_queue.py). **Ressources :** file SQLite de capacité dix.

```bash
python3 -m pocs.run 04b
```

Trente travaux arrivent. Dix reçoivent un équivalent `202` après persistance ; vingt sont refusés par un équivalent `429`. Un consommateur ouvre ensuite une nouvelle connexion et termine les dix travaux persistés. La file du POC ne modélise pas encore plusieurs workers, les baux d'exécution ou la durée des tâches.

**Extension réelle :** service d'export de rapports, broker durable ou table de jobs PostgreSQL, workers idempotents, statut consultable et stockage objet. Tester un crash après effet mais avant ACK ; ajouter une inbox, une expiration de bail, un nombre maximal d'essais et une file d'erreurs. Ne pas répondre `202` avant confirmation du stockage durable.

## Autoscaling et coût

Kubernetes HPA ajuste le nombre de réplicas à partir de métriques ; c'est une boucle de contrôle, avec un délai de réaction. Le CPU seul ne révèle pas toujours une file bloquée en entrée/sortie. [Documentation HPA](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/).

Fixer minimum, maximum, marge de capacité et règles de retour à la normale. Si le débit d'arrivée dépasse durablement la capacité de traitement, une file seule ne résout rien. Il faut augmenter la capacité, réduire le travail, décaler ou refuser.

Comparer le **coût pour 1 000 opérations réussies dans le délai cible**, en incluant base, réseau, cache, stockage et exploitation. Le sharding peut distribuer les écritures, mais complique les transactions et la répartition des clés ; l'introduire après avoir établi le besoin.

## Plan de validation

Monter progressivement la charge, tenir un palier, injecter un pic et observer le retour au calme. Mesurer débit tenté, accepté, terminé et refusé séparément ; p95/p99, files, saturation et invariants. Une moyenne rapide masque des requêtes très lentes. Les 32 threads du POC ne constituent pas un benchmark de capacité réelle.

Exercice : faut-il doubler les serveurs si le CPU API est à 20 % mais la base attend sur un verrou ? **Non sans traiter la contention.** Livrable : hypothèses de trafic, profil de charge, graphe de latence et décision coût/capacité.
