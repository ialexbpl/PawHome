# Deployment Plan (Argo CD + external PostgreSQL)

## Goal
Deploy PawHome web app on a 3-node Ubuntu k3s cluster with Argo CD, while PostgreSQL 18 runs in Docker on a VM.

## Pre-checks
1. Verify cluster and nodes:
   - `kubectl get nodes -o wide`
2. Verify Argo CD namespace exists:
   - `kubectl get ns argocd`
3. Verify control-plane node can reach VM PostgreSQL host on TCP 5432.

## Required Repo Settings
1. Start PostgreSQL on VM (Docker) and initialize schema:
   - `docker run ... -v pawhome-pgdata:/var/lib/postgresql postgres:18`
   - `cat sql/create_schema.sql sql/seed_dictionaries.sql | docker exec -i pawhome-postgres psql -U postgres -d pawhome`
2. Set a real DB password in `k8s/postgres-secret.yaml`.
3. Set external DB host in `k8s/web-deployment-service.yaml` (`DB_HOST`).
4. Set your app image tag in `k8s/web-deployment-service.yaml`:
   - `ghcr.io/ialexbpl/pawhome:<tag>`
5. Confirm Argo source repository in `argocd/pawhome-application.yaml`:
   - `spec.source.repoURL`
   - `spec.source.targetRevision`

## Bootstrap Argo Application
Apply once:

```bash
kubectl apply -f argocd/pawhome-application.yaml -n argocd
```

## Validate Deployment
1. Argo app status:
   - `kubectl get application -n argocd`
2. Workload status:
   - `kubectl -n pawhome get pods,svc`
3. Check app can connect to external DB in logs.
4. Check web app logs:
   - `kubectl -n pawhome logs deployment/pawhome-web`

## Troubleshooting
1. If image is private, create `regcred` and add `imagePullSecrets` to web Deployment.
2. If `LoadBalancer` has no external IP, verify MetalLB installation and pool configuration.
3. If app cannot connect to DB, verify VM firewall and network ACLs allow `5432/tcp` from cluster nodes.
