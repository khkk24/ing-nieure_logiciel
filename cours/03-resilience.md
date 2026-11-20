# 03 — Résilience : survivre à une panne sans inventer un succès

## Objectifs et prérequis

Distinguer atomicité, reprise et continuité de service ; contenir une dépendance défaillante ; définir ce qu'une panne peut faire perdre. Prérequis : cours 01 et 02. Durée indicative : 6 à 10 h.

## Deux problèmes derrière le mot « panne »

Dans un virement, débiter A puis tomber avant de créditer B menace l'intégrité des données. Dans une application surchargée, attendre une base inaccessible avec des milliers de connexions menace la disponibilité de tout le service. Les remèdes se complètent mais ne sont pas interchangeables.

**Invariant financier local :** pour ce transfert sans frais, la somme A + B reste constante. **Invariant de protection :** le nombre de ressources occupées à attendre une dépendance reste borné.

Si A et B sont dans la même base, effectuer débit, crédit, contrôle de solde et inscription de l'opération dans une transaction. Le moteur annule les changements non validés ou récupère les changements validés selon son mécanisme de journalisation et ses garanties de stockage. Le WAL de PostgreSQL journalise avant les pages de données et sert à la récupération après crash. [Documentation WAL](https://www.postgresql.org/docs/current/wal-intro.html).

Si les comptes appartiennent à deux systèmes indépendants, une transaction locale ne suffit plus : étudier les états intermédiaires et le rapprochement au défi 06. Une compensation est une nouvelle opération ; elle n'efface pas l'histoire.

## POC A — Interrompre réellement un virement

**Code :** [p03a_transfer.py](../pocs/p03a_transfer.py). **Ressources :** SQLite sur disque temporaire et sous-processus Python.

```bash
python3 -m pocs.run 03a
```

1. Initialiser A à 10 000 centimes et B à 0.
2. Le sous-processus débite 1 000 puis s'arrête brutalement avant commit.
3. Une nouvelle connexion retrouve A = 10 000, B = 0.
4. Une seconde exécution débite, crédite, valide et s'arrête avant de répondre.
5. Une nouvelle lecture retrouve A = 9 000, B = 1 000.

Résultat : total constant et distinction visible entre panne avant/après commit. Ce test couvre la mort du processus applicatif ; il ne simule pas une destruction de disque, une panne électrique ou un basculement de réplica.

**Extension réelle :** PostgreSQL, journal comptable en partie double, identifiant de virement unique et contraintes métier. Tester plusieurs arrêts aux frontières de transaction. Pour une panne du serveur de base, tester restauration et basculement sur une instance de laboratoire, puis vérifier les écritures acquittées selon le mode de réplication choisi.

## POC B — Couper temporairement les appels qui échouent

**Code :** [p03b_breaker.py](../pocs/p03b_breaker.py). **Ressources :** horloge simulée, aucune attente réseau.

```bash
python3 -m pocs.run 03b
```

Le circuit breaker laisse d'abord passer les appels. Après trois erreurs, il s'ouvre : les demandes suivantes obtiennent une réponse dégradée immédiate. Après un délai, un nouvel essai réussit et referme le circuit. Résultat : trois appels vers la dépendance au lieu de cent pendant la panne.

**Extension réelle :** API de catalogue + service de recommandation lent. Fixer un budget de temps global, des délais de connexion/lecture, un nombre maximal d'appels concurrents et un seul essai de reprise en état semi-ouvert. Servir le catalogue sans recommandations. Pour un paiement inconnu, afficher « vérification en cours », jamais un faux succès ou un faux refus définitif.

Le POC séquentiel ne gère pas plusieurs sondes de reprise concurrentes. La version réelle devra coordonner cette phase au niveau approprié et mesurer les timeouts réels.

## Les mécanismes complémentaires

| Mécanisme | Fonction | Piège |
|---|---|---|
| Timeout | Borner l'attente | Ne prouve pas l'absence d'effet |
| Retry avec backoff et jitter | Réessayer une panne transitoire en décalant les appels | Amplifie la charge sans budget ni idempotence |
| Circuit breaker | Cesser d'insister temporairement | Reprise brutale si trop de sondes |
| Bulkhead | Réserver des capacités par dépendance | Mauvais dimensionnement des compartiments |
| Sauvegarde et restauration | Récupérer après corruption ou perte | Une sauvegarde jamais restaurée reste non vérifiée |

AWS décrit l'usage combiné des délais et reprises espacées pour éviter l'amplification des pannes. [AWS Builders' Library](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/).

## Mesurer et conclure

Définir **RPO** : quantité de données perdables, et **RTO** : délai de rétablissement visé. Une réplication asynchrone peut perdre des commits récents lors d'un basculement ; une réplication synchrone impose d'autres compromis de latence et de disponibilité.

Suivre erreurs, temps d'attente, connexions actives, état des circuits, âge des opérations inconnues et durée d'une restauration. « Aucune perte possible » est trop vague : préciser quelles pannes, quels acquittements et quelles copies sont couverts.

Exercice : pourquoi trois retries à chacun de trois étages sont-ils dangereux ? **Ils peuvent multiplier les tentatives jusqu'à 27 au dernier étage.** Livrable : scénario de panne, budget de temps, invariant comptable et procédure de reprise démontrée.
