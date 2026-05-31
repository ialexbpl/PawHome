# Backlog

## Done
- [x] Add Kubernetes namespace manifest for isolated deployment (`k8s/namespace.yaml`).
- [x] Add PostgreSQL Kubernetes manifests with persistent storage and internal service (`k8s/postgres.yaml`).
- [x] Add Flask app Kubernetes manifests wired to PostgreSQL service and secret (`k8s/app.yaml`).
- [x] Add one-command PowerShell push and deploy workflow for Docker image + Kubernetes resources (`scripts/push-and-deploy.ps1`).
- [x] Convert Kubernetes deployment to GitOps-friendly declarative resources for Argo CD (`k8s/kustomization.yaml`).
- [x] Add declarative DB init ConfigMap and DB secret manifest for sync-based deploys (`k8s/db-init-configmap.yaml`, `k8s/postgres-secret.yaml`).
- [x] Add Argo CD `Application` manifest template for one-command bootstrap (`argocd/pawhome-application.yaml`).
- [x] Add repository `.gitignore` for Python, local env files, and generated artifacts.
- [x] Refocus README to lead with CI/CD and Kubernetes GitOps deployment workflow.

## Next
- [ ] Add ingress manifest (or gateway) for stable external access without port-forward.
- [ ] Add horizontal pod autoscaling for the web deployment.
- [ ] Add backup/restore strategy for PostgreSQL PVC data.
- [ ] Add CI pipeline job that builds, pushes, and deploys to Kubernetes automatically.
- [ ] Replace plain Secret with Sealed Secrets or External Secrets for safer Git storage.
