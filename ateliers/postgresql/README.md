# Atelier : concurrence sur PostgreSQL

Cet atelier complète le POC 01a avec le moteur destiné à une application serveur. **Préparé mais non exécuté ici.** Il ouvre vingt sessions concurrentes par le client `psql` du conteneur ; le démarrage des sessions n'est pas parfaitement simultané et ce n'est pas un benchmark de débit.

## Lancer

Prérequis : Docker fonctionnel, plugin Compose récent prenant en charge `--wait`, Python. Depuis la racine du dépôt :

```bash
docker compose -f ateliers/postgresql/compose.yaml up -d --wait
python3 ateliers/postgresql/race.py
```

Le script réinitialise uniquement les tables `ticket` et `sales` de la base de laboratoire `defis_lab` de ce projet Compose. Ne pas y placer de données personnelles. Aucun port PostgreSQL n'est publié sur l'hôte. Le mot de passe fourni est une valeur publique de démonstration, impropre à un service partagé.

Résultat attendu : `OK PostgreSQL : 20 tentatives, une vente, stock final nul.` La décrémentation et l'insertion de vente appartiennent à la même instruction SQL. Un échec de l'insertion annule aussi la décrémentation.

## Examiner puis expérimenter

```bash
docker compose -f ateliers/postgresql/compose.yaml exec db psql -U lab -d defis_lab
```

Dans le client SQL :

```sql
TABLE ticket;
TABLE sales;
SELECT pid, wait_event_type, wait_event, state
FROM pg_stat_activity WHERE datname = 'defis_lab';
```

Ouvrir deux terminaux SQL. Dans le premier, démarrer une transaction, verrouiller la ligne avec `SELECT * FROM ticket FOR UPDATE;`, et conserver la transaction ouverte. Dans le second, faire la même demande avec `SET lock_timeout = '2s';`. Observer l'attente puis l'expiration. Terminer les transactions avec `ROLLBACK;`. Ces manipulations ne sont pas requises par le test automatique.

Modifier ensuite la capacité initiale du script et son résultat attendu pour dix tickets. Ajouter un identifiant de commande unique pour étudier les répétitions. Mesurer séparément attente de verrou et durée d'exécution.

## Arrêter

```bash
docker compose -f ateliers/postgresql/compose.yaml down
```

Le volume est conservé. Ne supprimer le volume qu'après avoir décidé de jeter les données du laboratoire.

Image utilisée : version 17.12, publiée dans le catalogue consulté ; pour une reproductibilité de distribution, enregistrer également le digest après téléchargement. [Image PostgreSQL officielle](https://hub.docker.com/_/postgres).
