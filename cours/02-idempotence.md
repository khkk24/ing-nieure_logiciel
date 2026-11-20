# 02 — Idempotence : une intention, un seul effet métier

## Objectifs et prérequis

Concevoir une commande rejouable, gérer les réponses perdues et traiter les messages dupliqués. Prérequis : transactions et concurrence. Durée indicative : 6 à 8 h.

## Comprendre le paiement fantôme

Le serveur a enregistré un débit. La réponse disparaît. Le client affiche une erreur et renvoie la demande. Si chaque requête représente un nouveau débit, le compte est débité deux fois.

L'idempotence signifie que rejouer **la même intention** ne produit pas un nouvel effet. Deux achats distincts de 10 € doivent rester possibles. Dédupliquer uniquement par montant, par utilisateur ou par une courte fenêtre temporelle serait donc incorrect.

Une méthode HTTP et une garantie métier sont deux choses distinctes. Un `POST` peut devenir rejouable grâce à un contrat d'idempotence. Un `GET` censé lire ne devrait pas déclencher une opération d'achat.

**Invariant :** au plus un effet validé pour `(identité, opération, clé)`, et résultat stable selon le contrat documenté.

## La conception pas à pas

Le client crée une clé avant le premier envoi et la conserve jusqu'à résolution. Le serveur vérifie l'identité, calcule une empreinte canonique du contenu pertinent, puis enregistre la clé, l'effet et le résultat dans une transaction lorsqu'ils appartiennent à la même base.

La clé porte une contrainte d'unicité. Une requête identique retrouve le résultat ; une même clé avec un autre montant provoque un conflit. Le contenu canonique doit inclure devise, montant en unité entière, destinataire et paramètres ayant un effet métier. La clé n'est jamais une preuve d'autorisation.

Avec un prestataire externe, il n'existe pas de transaction locale englobant magiquement son système. Il faut une clé persistée chez soi, une clé stable transmise au prestataire, un état `PENDING/UNKNOWN/SUCCEEDED/FAILED`, et un rapprochement par consultation ou événement. Un timeout n'autorise pas à déclarer l'échec définitif et à créer une autre clé.

Stripe documente la réutilisation d'une clé pour les requêtes répétées et le contrôle des paramètres. Les contrats diffèrent entre versions d'API ; il faut lire celui réellement intégré et tenir compte de la durée de conservation des clés. [Documentation Stripe](https://docs.stripe.com/api/idempotent_requests).

## POC A — Réponse perdue après un débit local

**Code :** [p02a_idempotence.py](../pocs/p02a_idempotence.py). **Ressources :** SQLite et 12 threads ; aucun accès bancaire.

```bash
python3 -m pocs.run 02a
```

Le premier appel valide son effet, mais le programme ignore sa réponse. Douze appels réutilisent la même clé. Un treizième essai modifie le montant. Résultat attendu : un seul débit, des réponses identiques pour les reprises valides et un rejet du contenu différent.

Le verrou transactionnel SQLite simplifie la sérialisation. Sur PostgreSQL, utiliser l'unicité et traiter correctement la compétition sur l'insertion, puis relire le résultat après résolution de la transaction concurrente.

**Extension réelle :** `POST /payments` avec en-tête `Idempotency-Key`, PostgreSQL et simulateur de prestataire séparé. Couper la réponse du simulateur après capture. Redémarrer l'API, rejouer et rapprocher l'état sans second débit. Ajouter un test de même clé utilisée par deux utilisateurs : leurs espaces doivent être distincts.

## POC B — Événement de fidélité livré deux fois

**Code :** [p02b_inbox.py](../pocs/p02b_inbox.py). **Ressources :** SQLite, table inbox et compteur de points.

```bash
python3 -m pocs.run 02b
```

Le consommateur tente d'inscrire un identifiant d'événement dans son inbox. Une panne survient avant l'ajout de points : la transaction annule les deux modifications. Le message revient, les points sont ajoutés, puis une livraison supplémentaire est ignorée. Résultat : 10 points, pas 20.

**Extension réelle :** broker durable et consommateur de commandes payées ; accuser réception après le commit local. Si le processus meurt après commit mais avant ACK, l'inbox protège le rejeu. Tester deux consommateurs concurrents, un message malformé et une file d'erreurs inspectable.

## Limites et pièges

Une table de déduplication consultée puis mise à jour hors transaction possède elle-même une course critique. Une clé conservée seulement en mémoire disparaît au redémarrage. Une suppression trop précoce des clés permet à un vieux rejeu de refaire l'effet. Une clé stable n'empêche pas deux commandes différentes de demander le dernier billet : le défi 01 reste nécessaire.

L'inbox protège l'effet dans sa transaction locale. Elle ne rend pas un e-mail ou un appel externe atomique. Pour cela, utiliser une outbox et, si possible, la déduplication du destinataire.

Mesurer doublons reçus, conflits de clés, opérations `UNKNOWN` anciennes et durée de rapprochement. Conserver les identifiants de corrélation sans journaliser les données de paiement sensibles.

## Exercice corrigé et livrable

Un utilisateur clique volontairement deux fois pour acheter deux billets. Même clé ? **Non : deux intentions, deux clés.** Son premier achat est encore inconnu et il recharge la page ? **Même clé et consultation de l'état.**

Livrable : contrat HTTP, portée et conservation des clés, états de paiement, test de réponse perdue, test de paramètres modifiés. Relier ce cours à [l'outbox et aux sagas](06-fiabilite.md).
