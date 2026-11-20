# Compte rendu d'un défi

Copier ce document pour chaque défi, puis remplir les sections avec des observations.

## 1. Besoin métier

Qui utilise le service ? Quelle action réalise-t-il ? Quelle erreur lui ferait du tort ?

## 2. Invariant et hypothèses

Écrire une propriété vérifiable. Nommer l'autorité des données, les pannes couvertes, les pannes exclues et le comportement dégradé acceptable.

## 3. Contre-exemple

Décrire, étape par étape, l'exécution qui casse la solution naïve. Indiquer où les requêtes se chevauchent ou où le processus tombe.

## 4. POC A et POC B

Pour chaque POC : commande exacte, version du runtime, état initial, panne injectée, résultat attendu, résultat observé et fichier de preuve.

## 5. Décision d'architecture

Comparer au moins deux options : garantie, coût, complexité, latence, exploitation et évolutivité. Expliquer pourquoi la solution choisie est suffisante pour ce besoin.

## 6. Validation adverse

Que se passe-t-il après duplication, changement d'ordre, réponse perdue, entrée invalide et redémarrage ? Quels cas restent non testés ?

## 7. Passage à un service réel

Décrire API, tables, contraintes, transactions, identités, métriques, mécanisme de reprise et procédure opérateur. Distinguer ce qui est déjà implémenté de l'extension à réaliser.

## 8. Autoévaluation

| Critère | Acquis ? | Preuve |
|---|---|---|
| Je peux expliquer la panne sans nom d'outil | | |
| Mon invariant est mesurable | | |
| Je peux montrer un contre-exemple | | |
| Les deux POC sont reproductibles | | |
| Je connais les limites de la solution | | |
| Je sais quelle métrique alerterait en production | | |
