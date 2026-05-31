param(
    [Parameter(Mandatory = $true)]
    [string]$ImageRepo,

    [Parameter(Mandatory = $false)]
    [string]$ImageTag = "latest",

    [Parameter(Mandatory = $false)]
    [string]$DbPassword = "change-me-now"
)

$ErrorActionPreference = "Stop"
$image = "$ImageRepo`:$ImageTag"

Write-Host "==> Building Docker image: $image"
docker build -t $image .

Write-Host "==> Pushing Docker image"
docker push $image

Write-Host "==> Creating namespace"
kubectl apply -f k8s/namespace-pawhome.yaml

Write-Host "==> Creating SQL init ConfigMap"
kubectl -n pawhome create configmap pawhome-db-init `
  --from-file=sql/create_schema.sql `
  --from-file=sql/seed_dictionaries.sql `
  --dry-run=client -o yaml | kubectl apply -f -

Write-Host "==> Creating/Updating DB secret"
kubectl -n pawhome create secret generic pawhome-postgres-secret `
  --from-literal=POSTGRES_PASSWORD="$DbPassword" `
  --dry-run=client -o yaml | kubectl apply -f -

Write-Host "==> Deploying PostgreSQL"
kubectl apply -f k8s/postgres-statefulset-pvc-service.yaml

Write-Host "==> Deploying Flask app"
kubectl apply -f k8s/web-deployment-service.yaml

Write-Host "==> Setting app image to $image"
kubectl -n pawhome set image deployment/pawhome-web pawhome-web=$image

Write-Host "==> Waiting for rollouts"
kubectl -n pawhome rollout status statefulset/pawhome-postgres --timeout=240s
kubectl -n pawhome rollout status deployment/pawhome-web --timeout=240s

Write-Host "`nDeployment complete."
Write-Host "Run this to access app locally:"
Write-Host "kubectl -n pawhome port-forward svc/pawhome-web 5000:5000"
