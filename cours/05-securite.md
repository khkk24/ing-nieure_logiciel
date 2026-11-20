# 05 — Sécurité : contrôler l'accès à chaque ressource

## Objectifs et prérequis

Distinguer authentification et autorisation, empêcher l'accès par modification d'identifiant, puis isoler plusieurs organisations. Prérequis : HTTP, SQL paramétré, tests. Durée indicative : 6 à 10 h.

## Pourquoi connaître un ID ne donne aucun droit

Alice demande sa facture `/invoices/inv-a`. Elle remplace l'identifiant par celui de Bob. Si l'API se contente de chercher la facture par ID, elle la divulgue. Le serveur a bien reconnu Alice ; il n'a pas vérifié son droit sur **cet objet**.

L'authentification répond « qui es-tu ? ». L'autorisation répond « cette identité peut-elle réaliser cette action sur cet objet, dans cette organisation et dans ce contexte ? ». Un identifiant imprévisible réduit la découverte facile des objets ; il ne constitue pas un contrôle d'accès.

OWASP classe cette faille comme Broken Object Level Authorization et rappelle qu'elle existe aussi avec des UUID. [OWASP API1](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/).

**Invariant :** aucune lecture ni mutation ne traverse une frontière d'accès sans une permission explicite. Les endpoints de liste, export, pièces jointes, recherche et traitement en lot comptent autant que `GET /resource/id`.

## Mettre la décision au bon endroit

L'identité vient d'une session ou d'un jeton vérifié côté serveur : signature, émetteur, audience, expiration et politique de révocation adaptée. Le `user_id` fourni par le client ne remplace pas cette identité.

La requête SQL peut porter la restriction directement :

```sql
SELECT amount FROM invoices
WHERE id = :invoice_id AND owner_id = :authenticated_user_id;
```

Pour modifier, porter également l'autorisation dans la requête ou la même transaction afin d'éviter qu'un contrôle antérieur devienne périmé. Refuser par défaut les actions inconnues. Les rôles simplifient des groupes de permissions, mais « admin d'une clinique » ne signifie pas « admin de toutes les cliniques ».

## POC A — Accéder à une facture privée

**Code :** [p05a_ownership.py](../pocs/p05a_ownership.py). **Ressources :** SQLite, deux propriétaires fictifs ; l'identité est déjà considérée comme authentifiée.

```bash
python3 -m pocs.run 05a
```

Alice lit sa facture. Une demande portant l'ID de Bob ne renvoie rien. Un identifiant contenant une tentative d'injection ne modifie pas le SQL, grâce au paramétrage. Deux protections différentes sont illustrées : autorisation sur l'objet et séparation du code SQL et des valeurs.

**Extension réelle :** API avec sessions, endpoints GET/PATCH/DELETE et téléchargement. Tester Alice, Bob, un visiteur anonyme et un compte suspendu pour chaque opération. Le statut `404` peut masquer l'existence de la ressource ; définir une politique cohérente, sans considérer ce masquage comme la protection principale.

## POC B — Administrateur limité à son organisation

**Code :** [p05b_tenant.py](../pocs/p05b_tenant.py). **Ressources :** politique pure testable, rôles lecteur/éditeur/admin.

```bash
python3 -m pocs.run 05b
```

Un admin de A peut supprimer un objet de A. Il ne peut pas lire celui de B. Un lecteur ne peut pas supprimer ; une action inconnue est refusée. Le POC teste le moteur de décision, sans fournisseur d'identité ni route HTTP.

**Extension réelle :** SaaS de gestion de cliniques, organisations et appartenances stockées en base, règles serveur et PostgreSQL Row-Level Security comme seconde barrière. Une politique RLS filtre les lignes ; elle ne dispense pas du contrôle d'accès applicatif. Les propriétaires, superutilisateurs et rôles `BYPASSRLS` nécessitent une attention particulière. [Documentation RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html).

Utiliser un rôle applicatif limité, définir le contexte d'organisation depuis une identité vérifiée et le limiter à la transaction pour éviter les fuites entre connexions du pool. Le client ne doit jamais choisir librement une organisation à laquelle il n'appartient pas.

## Une défense plus large

Cet axe ne couvre pas toute la sécurité. Ajouter TLS, secrets hors du dépôt, validation des entrées, limitation de débit, permissions minimales, journal d'audit, mises à jour de dépendances et authentification renforcée des comptes sensibles. Avec des cookies de session, prendre aussi en compte CSRF et les attributs appropriés. Ne pas donner à l'API le rôle de propriétaire de toutes ses tables par facilité.

Les caches doivent inclure le contexte d'autorisation ou ne stocker que des données réellement publiques. Un cache global indexé seulement par l'URL peut divulguer une réponse privée pourtant correctement filtrée à l'origine.

## Validation et exercice

Construire une matrice identité × organisation × objet × action. Inclure lecture, création, mutation, export, méthodes HTTP modifiées, propriétés administratives injectées et changement de propriétaire. Vérifier les refus **et l'absence d'effet**, pas seulement le code HTTP.

Exercice : cacher le bouton « supprimer » suffit-il ? **Non : une requête peut être envoyée sans l'interface.** Le rôle admin suffit-il ? **Non : sa portée doit être définie.**

Livrable : matrice d'accès, tests d'isolation, schéma de propagation de l'identité et règles d'audit sans données privées inutiles. Les exemples de cliniques sont des cas d'application pédagogiques, sans données de patients.
