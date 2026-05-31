# Deployment Plan (Argo CD + k3s)

## Goal
Deploy PawHome on a 3-node Ubuntu k3s cluster with Argo CD and PostgreSQL 18.

## Pre-checks
1. Verify cluster and nodes:
   - `kubectl get nodes -o wide`
2. Verify Argo CD namespace exists:
   - `kubectl get ns argocd`
3. Verify default StorageClass exists (`local-path` for k3s):
   - `kubectl get storageclass`

## Required Repo Settings
1. Set a real DB password in `k8s/postgres-secret.yaml`.
2. Set your app image tag in `k8s/web-deployment-service.yaml`:
   - `ghcr.io/ialexbpl/pawhome:<tag>`
3. Confirm Argo source repository in `argocd/pawhome-application.yaml`:
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
   - `kubectl -n pawhome get pods,svc,pvc`
3. Check PostgreSQL boot logs:
   - `kubectl -n pawhome logs statefulset/pawhome-postgres`
4. Check web app logs:
   - `kubectl -n pawhome logs deployment/pawhome-web`

## Troubleshooting
1. If PostgreSQL used an older PVC layout, recreate the PVC:
   - `kubectl -n pawhome delete pvc pawhome-postgres-pvc`
2. If image is private, create `regcred` and add `imagePullSecrets` to web Deployment.
3. If `LoadBalancer` has no external IP, verify MetalLB installation and pool configuration.
