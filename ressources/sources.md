# Sources officielles et lectures

Références consultées le **18 novembre 2026**. Les liens `current` et `stable` peuvent évoluer ; relever la version utilisée lors des ateliers. Les explications et scénarios du parcours sont des synthèses pédagogiques originales ; les services fictifs ne sont pas présentés comme des architectures internes d'entreprises réelles.

| Cours | Source primaire | Utilisation |
|---|---|---|
| 01 | [PostgreSQL — verrous](https://www.postgresql.org/docs/current/explicit-locking.html) | Arbitrage des écritures concurrentes |
| 01 | [PostgreSQL 16 — isolation](https://www.postgresql.org/docs/16/transaction-iso.html) | Isolation et conflits de sérialisation |
| 02 | [Stripe — idempotence](https://docs.stripe.com/api/idempotent_requests) | Exemple réel de contrat d'API rejouable |
| 03 | [PostgreSQL — WAL](https://www.postgresql.org/docs/current/wal-intro.html) | Journalisation et récupération |
| 03 | [AWS — timeouts et retries](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) | Pratiques documentées de protection des dépendances |
| 04 | [Kubernetes — HPA](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/) | Ajustement de capacité |
| 05 | [OWASP — BOLA](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/) | Risque et contrôles par objet |
| 05 | [PostgreSQL — RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) | Isolation par politiques de lignes |
| 06 | [Chris Richardson — outbox](https://microservices.io/patterns/data/transactional-outbox.html) | Intention de publication atomique |
| 06 | [Debezium — outbox router](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html) | Implémentation moderne par capture de changements |
| 06 | [Temporal — workflows](https://docs.temporal.io/workflows) | Processus durables |
| 07 | [Kubernetes — rolling update](https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/) | Remplacement progressif |
| 07 | [Kubernetes — sondes](https://kubernetes.io/docs/concepts/workloads/pods/probes/) | Readiness, liveness, démarrage |
| 07 | [Kubernetes — cycle de vie](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination) | Terminaison des pods |
| 08 | [Yjs](https://docs.yjs.dev/) | Types collaboratifs et fusion |
| 08 | [Preguiça et al. — panorama CRDT](https://arxiv.org/abs/1806.10254) | Concepts et compromis des CRDT |
| 09 | [Légifrance — API et données](https://www.legifrance.gouv.fr/contenu/pied-de-page/open-data-et-api) | Exemple de source officielle pour une extension française |
| 09 | [OWASP — prompt injection](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) | Défense face aux instructions adverses |
| 09 | [NIST — AI 600-1](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) | Gestion des risques de l'IA générative |
| 10 | [Ongaro et Ousterhout — Raft](https://raft.github.io/raft.pdf) | Consensus et journal répliqué |
| 10 | [CockroachDB — réplication](https://www.cockroachlabs.com/docs/stable/architecture/replication-layer) | Exemple de moteur distribué utilisant Raft |
| Architecture | [FastAPI — déploiement](https://fastapi.tiangolo.com/deployment/concepts/) | Processus et exploitation d'une API Python |
| Architecture | [OpenTelemetry — signaux](https://opentelemetry.io/docs/concepts/signals/) | Traces, métriques et logs |
| Architecture | [pgvector](https://github.com/pgvector/pgvector) | Recherche vectorielle dans PostgreSQL |
| Ateliers | [PostgreSQL officiel](https://hub.docker.com/_/postgres), [Nginx officiel](https://hub.docker.com/_/nginx), [BusyBox officiel](https://hub.docker.com/_/busybox) | Images de laboratoire |

## Cas d'application et réalité des exemples

Les factures de SaaS, billets de concert, inspections de terrain, budgets régionaux et commandes de boutique sont des **transpositions de besoins réels en cas pédagogiques**. Ils ne sont pas des études affirmant qu'une entreprise nommée emploie exactement notre implémentation.

Les références nommées ci-dessus montrent des pratiques ou implémentations effectivement documentées : contrat d'idempotence Stripe, pratiques de reprises AWS, contrôles PostgreSQL, orchestration Kubernetes, outbox Debezium, workflows Temporal, fusion Yjs et réplication CockroachDB. Lire leurs contraintes avant toute adoption.
