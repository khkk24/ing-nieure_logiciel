# Atelier : observer un rollout avec du trafic

**Préparé mais non exécuté ici.** Prérequis : `kubectl`, cluster Kubernetes local existant et suffisamment de place pour trois petits pods. Utiliser un contexte de laboratoire ; ces commandes appliquent des ressources au contexte sélectionné.

## Préparer et vérifier le contexte

```bash
kubectl config current-context
kubectl apply -f ateliers/kubernetes/deployment.yaml
kubectl -n defis-lab rollout status deployment/demo --timeout=120s
kubectl -n defis-lab get pods
```

Le manifeste expose uniquement un Service interne au cluster. `maxUnavailable: 0` garde les anciens pods pendant l'arrivée de nouveaux pods prêts, sous réserve de leur santé et de la capacité du cluster. Le tag `stable-alpine` est mutable : enregistrer les digests réellement exécutés pour comparer deux essais. Ce serveur statique est un support de laboratoire, pas le serveur de paiement des autres cours.

## Observer des requêtes pendant le changement

Créer le client dans le cluster pour tester le Service plutôt qu'un port-forward attaché à un pod particulier :

```bash
kubectl -n defis-lab run probe --image=busybox:1.37.0 --restart=Never --command -- sh -c 'i=0; while [ "$i" -lt 300 ]; do if wget -q -T 2 -O /dev/null http://demo; then echo OK; else echo ECHEC; fi; i=$((i+1)); sleep 1; done'
kubectl -n defis-lab logs -f probe
```

Dans un autre terminal, déclencher le remplacement des pods en changeant leur template :

```bash
kubectl -n defis-lab set env deployment/demo DEMO_REV=2
kubectl -n defis-lab rollout status deployment/demo --timeout=120s
kubectl -n defis-lab get pods
```

L'environnement `DEMO_REV` provoque un rollout mais ne modifie pas la page Nginx. Pour un vrai changement fonctionnel, construire deux versions de son API et appliquer leurs images identifiées par digest. Résultat visé de cet essai : zéro `ECHEC` parmi les requêtes observées. Un essai réussi n'est pas une preuve universelle de zéro interruption, et un appel par seconde peut manquer une coupure très courte.

Le hook `preStop` attend puis demande un arrêt gracieux de Nginx. Ce délai fixe illustre la propagation du retrait ; il faut le mesurer sur l'infrastructure cible. Les sondes de ce serveur statique ne prouvent pas la santé d'une application dépendant de plusieurs systèmes.

## Retour arrière

```bash
kubectl -n defis-lab rollout undo deployment/demo
kubectl -n defis-lab rollout status deployment/demo --timeout=120s
```

Observer encore les requêtes. Une migration de base incompatible ne serait pas annulée par cette commande. Voir le POC 07b.

## Nettoyage facultatif

Après conservation des résultats, les deux commandes suivantes suppriment exclusivement les ressources de ce laboratoire :

```bash
kubectl -n defis-lab delete pod probe
kubectl delete -f ateliers/kubernetes/deployment.yaml
```

Le fichier contient aussi le Namespace : sa suppression détruit toute autre ressource qui aurait été placée dans `defis-lab`. Ne pas y placer de travaux à conserver.

Sources : [sondes Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/probes/), [terminaison des pods](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination), [image Nginx](https://hub.docker.com/_/nginx), [image BusyBox](https://hub.docker.com/_/busybox).
