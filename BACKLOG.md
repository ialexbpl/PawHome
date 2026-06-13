# Backlog

## Done
- [x] Add Kubernetes namespace manifest for isolated deployment (`k8s/namespace-pawhome.yaml`).
- [x] Add PostgreSQL Kubernetes manifests with persistent storage and internal service (`k8s/postgres-statefulset-pvc-service.yaml`).
- [x] Add Flask app Kubernetes manifests wired to PostgreSQL service and secret (`k8s/web-deployment-service.yaml`).
- [x] Add one-command PowerShell push and deploy workflow for Docker image + Kubernetes resources (`scripts/push-and-deploy.ps1`).
- [x] Convert Kubernetes deployment to GitOps-friendly declarative resources for Argo CD (`k8s/kustomization.yaml`).
- [x] Add declarative DB init ConfigMap and DB secret manifest for sync-based deploys (`k8s/db-init-configmap.yaml`, `k8s/postgres-secret.yaml`).
- [x] Add Argo CD `Application` manifest template for one-command bootstrap (`argocd/pawhome-application.yaml`).
- [x] Add repository `.gitignore` for Python, local env files, and generated artifacts.
- [x] Refocus README to lead with CI/CD and Kubernetes GitOps deployment workflow.
- [x] Expose app service as MetalLB `LoadBalancer` for external cluster access (`k8s/web-deployment-service.yaml`).
- [x] Standardize PostgreSQL storage on k3s default dynamic provisioning (`local-path`) for multi-node compatibility (`k8s/postgres-statefulset-pvc-service.yaml`).
- [x] Remove Docker Compose file to keep repository Kubernetes/Argo focused.
- [x] Align README deployment path to k3s + Argo CD + MetalLB with GHCR pull-secret flow.
- [x] Upgrade Kubernetes PostgreSQL runtime image from `postgres:16` to `postgres:18`.
- [x] Add `DEPLOYMENT_PLAN.md` with clean end-to-end k3s + Argo runbook.
- [x] Harden app and DB probes for cluster startup sequencing (`app.py`, `k8s/web-deployment-service.yaml`, `k8s/postgres-statefulset-pvc-service.yaml`).
- [x] Make Argo deployment multi-node friendly by using `local-path` PVC and removing mandatory private registry secret (`k8s/kustomization.yaml`, `k8s/postgres-statefulset-pvc-service.yaml`, `k8s/web-deployment-service.yaml`, `argocd/pawhome-application.yaml`).
- [x] Remove legacy static PV and generated export/performance artifacts from git-tracked content (`k8s/postgres-pv.yaml`, `exports/`, `analysis/performance_results.md`).
- [x] Add missing environment template and align deployment runbook/docs with current manifests (`.env.example`, `DEPLOYMENT_PLAN.md`, `README.md`).
- [x] Refactor deployment model to app-only Kubernetes with external PostgreSQL (Docker on VM) and remove in-cluster DB manifests (`k8s/kustomization.yaml`, `k8s/web-deployment-service.yaml`, `scripts/push-and-deploy.ps1`, `README.md`, `DEPLOYMENT_PLAN.md`).
- [x] Remove obsolete in-cluster PostgreSQL resources from repo (`k8s/postgres-statefulset-pvc-service.yaml`, `k8s/db-init-configmap.yaml`).
- [x] Add explicit README runbook for pushing repo changes and syncing Argo CD state (`README.md`).

## Next
- [ ] Add ingress manifest (or gateway) for stable external access without port-forward.
- [ ] Add horizontal pod autoscaling for the web deployment.
- [ ] Add backup/restore strategy for external Docker PostgreSQL data volume.
- [ ] Add CI pipeline job that builds, pushes, and deploys to Kubernetes automatically.
- [ ] Replace plain Secret with Sealed Secrets or External Secrets for safer Git storage.
- [ ] Add Ingress + TLS (cert-manager) so app is reachable via DNS instead of bare LoadBalancer IP.
