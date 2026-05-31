param(
    [Parameter(Mandatory = $true)]
    [string]$ImageRepo,

    [Parameter(Mandatory = $false)]
    [string]$ImageTag = "latest",

    [Parameter(Mandatory = $true)]
    [string]$DbHost,

    [Parameter(Mandatory = $true)]
    [string]$DbPassword
)

$ErrorActionPreference = "Stop"
$image = "$ImageRepo`:$ImageTag"

Write-Host "==> Building Docker image: $image"
docker build -t $image .

Write-Host "==> Pushing Docker image"
docker push $image

Write-Host "==> Creating namespace"
kubectl apply -f k8s/namespace-pawhome.yaml

Write-Host "==> Applying Kubernetes manifests from kustomize"
kubectl apply -k k8s

Write-Host "==> Creating/Updating DB secret"
kubectl -n pawhome create secret generic pawhome-postgres-secret `
  --from-literal=POSTGRES_PASSWORD="$DbPassword" `
  --dry-run=client -o yaml | kubectl apply -f -

Write-Host "==> Setting external DB host to $DbHost"
kubectl -n pawhome set env deployment/pawhome-web DB_HOST=$DbHost

Write-Host "==> Setting app image to $image"
kubectl -n pawhome set image deployment/pawhome-web pawhome-web=$image

Write-Host "==> Waiting for rollouts"
kubectl -n pawhome rollout status deployment/pawhome-web --timeout=240s

Write-Host "`nDeployment complete."
Write-Host "Run this to access app locally:"
Write-Host "kubectl -n pawhome port-forward svc/pawhome-web 5000:5000"
