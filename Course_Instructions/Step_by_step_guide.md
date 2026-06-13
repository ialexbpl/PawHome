# KUBERNETES DEPLOYMENT ON MAC OS INFRASTRUCTURE

```bash
# Naming perception

OPHWNODE03 OP-opole/city/location HW-hardware/vm NODE-position

```
## NODE SETUP + VIRTUALISATION

### 1. Przygotowanie hostów macOS

```bash
# Na każdym Mac Pro:

# 1a. Sudo bez hasła dla admin
echo 'admin ALL=(ALL) NOPASSWD: ALL' | sudo tee /etc/sudoers.d/admin

# 1b. Wyłączenie usypiania
sudo pmset -a sleep 0 displaysleep 0 disksleep 0

# 1c. Ustawienie hostname
sudo scutil --set ComputerName OPHWNODE03
sudo scutil --set HostName OPHWNODE03
sudo scutil --set LocalHostName OPHWNODE03

# 1d. Homebrew + Lima + socket_vmnet
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install lima
brew install socket_vmnet
sudo brew services start socket_vmnet
```

### 2. Konfiguracja Lima networks.yaml

```bash
# Na każdym Mac Pro — ścieżka: ~/.lima/_config/networks.yaml
cat > ~/.lima/_config/networks.yaml << 'EOF'
paths:
  socketVMNet: "/opt/homebrew/socket_vmnet/bin/socket_vmnet"    ....COPY AND CHANGE PATHS!
  varRun: /private/var/run/lima
  sudoers: /private/etc/sudoers.d/lima

group: everyone

networks:
  bridged:
    mode: bridged
    interface: en1
EOF
```

### 3. Tworzenie VM z bridged networking

```bash

cat > ~/.lima/OPVMKUB02.yaml << 'EOF'
vmType: vz
arch: "aarch64"
cpus: 18
memory: "128GiB"
disk: "500GiB"

images:
  - location: "https://cloud-images.ubuntu.com/releases/24.04/release/ubuntu-24.04-server-cloudimg-arm64.img"
    arch: "aarch64"

networks:
  - lima: bridged
    interface: "bond0"

provision:
  - mode: system
    script: |
      #!/bin/bash
      set -eux
      echo 'net.ipv4.ip_forward=1' > /etc/sysctl.d/90-k8s.conf
      echo 'net.bridge.bridge-nf-call-iptables=1' >> /etc/sysctl.d/90-k8s.conf
      echo 'fs.inotify.max_user_instances=8192' >> /etc/sysctl.d/90-k8s.conf
      echo 'fs.inotify.max_user_watches=524288' >> /etc/sysctl.d/90-k8s.conf
      sysctl --system || true
      modprobe br_netfilter || true
      modprobe overlay || true
EOF

limactl create --name=OPVMKUB02 ~/.lima/OPVMKUB02.yaml --tty=false
limactl start OPVMKUB13... CHANGE PER VM
```
### 4. Statyczny IP w VM (netplan)

```bash
/opt/homebrew/bin/limactl shell OPVMKUB02 -- sudo bash -c '

cat > /etc/netplan/99-bridged-static.yaml << EOF
network:
  version: 2
  ethernets:
    bond0:
      dhcp4: false
      addresses: [10.1.1.2/16]
      routes:
        - to: 0.0.0.0/0
          via: 10.1.0.1
          metric: 50
      nameservers:
        addresses: [10.1.53.53, 8.8.8.8]
EOF
chmod 600 /etc/netplan/99-bridged-static.yaml
netplan apply
'
```

### 5. Optymalizacja routingu (internet przez VZ NAT)

```bash
# Domyślna trasa przez eth0 (szybki internet via VZ NAT)
# Sieć lokalna przez en1 (bridged, L2)
limactl shell OPVMKUB13 -- sudo bash -c '
ip route del default via $(ip route show default dev en1 | awk "{print \$3}") dev en1 2>/dev/null || true
ip route replace default via 192.168.5.2 dev eth0 metric 100
ip route replace 10.189.5.0/24 dev en1 src 10.189.5.41 metric 50
'
```

## VM + KUBERNETES CLUSTER
### 6. Bootstrap K3s on VM

```bash
# W VM 10.1.1.1, 2 ,3 ,4 ,5, 6, 7:
curl -Lo /tmp/k3s https://github.com/k3s-io/k3s/releases/download/v1.34.5%2Bk3s1/k3s-arm64
curl -Lo /tmp/install.sh https://get.k3s.io
chmod +x /tmp/k3s /tmp/install.sh


sudo cp /tmp/k3s /usr/local/bin/k3s

sudo chmod +x /usr/local/bin/k3s

INSTALL_K3S_SKIP_DOWNLOAD=true /tmp/install.sh

# Token klastra
sudo cat /var/lib/rancher/k3s/server/node-token


sudo sh -c "echo 'K107a6221367672da760cd706770b32413250c385d985a839b5417e530398a29c88::server:d6fbd7f32ad6346b839c7af7c0e26f54' > /etc/rancher/k3s/cluster-token"

# Konfiguracja
cd /etc/rancher/k3s/
la -al
sudo nano config.yaml

-INSIDE /etc/rancher/k3s/config.yaml

cluster-init: true
token-file: /etc/rancher/k3s/cluster-token
tls-san:
  - "10.1.1.2"
  - "10.1.1.10"
  - "10.1.1.16"
  - "k8s.zsel.opole.pl"
  - "127.0.0.1"
flannel-backend: "none"
disable-network-policy: true
disable-kube-proxy: true
disable:
  - traefik
  - servicelb
  - local-storage
cluster-cidr: "10.42.0.0/16"
service-cidr: "10.43.0.0/16"
cluster-dns: "10.43.0.10"
node-ip: "10.1.1.2"


node-external-ip: "10.1.1.2"
node-label:
  - "topology.kubernetes.io/zone=zsel-dc1"
kubelet-arg:
  - "max-pods=200"
  - "image-gc-high-threshold=85"
  - "image-gc-low-threshold=80"
etcd-snapshot-schedule-cron: "0 */6 * * *"
etcd-snapshot-retention: 10
write-kubeconfig-mode: "0644"
data-dir: /var/lib/rancher/k3s


sudo rm -rf /var/lib/rancher/k3s/server/db/etcd
INSTALL_K3S_SKIP_DOWNLOAD=true /tmp/install.sh
sudo systemctl daemon-reload
sudo systemctl restart k3s
sudo kubectl get nodes

```
### 7. Dołączanie workerów

```bash
# Na każdym workerze (VM):
curl -Lo /tmp/k3s https://github.com/k3s-io/k3s/releases/download/v1.34.5%2Bk3s1/k3s-arm64
curl -Lo /tmp/install.sh https://get.k3s.io
chmod +x /tmp/k3s /tmp/install.sh

sudo cp /tmp/k3s /usr/local/bin/k3s
sudo chmod +x /usr/local/bin/k3s

sudo mkdir /etc/rancher/
sudo mkdir /etc/rancher/k3s

sudo sh -c "echo 'K107a6221367672da760cd706770b32413250c385d985a839b5417e530398a29c88::server:d6fbd7f32ad6346b839c7af7c0e26f54' > /etc/rancher/k3s/cluster-token"



cd /etc/rancher/k3s/
sudo nano config.yaml

server: "https://10.1.1.2:6443"
token-file: /etc/rancher/k3s/cluster-token
node-ip: "10.1.1.10"
node-external-ip: "10.1.1.10"
node-label:
  - "topology.kubernetes.io/zone=zsel-dc1"
kubelet-arg:
  - "max-pods=200"
  - "image-gc-high-threshold=85"
  - "image-gc-low-threshold=80"
data-dir: /var/lib/rancher/k3s


sudo systemctl daemon-reload
sudo systemctl restart k3s-agent
sudo systemctl status k3s-agent
sudo kubectl get nodes

# UI Hubble if wanted
sudo kubectl port-forward -n kube-system svc/hubble-ui 12000:80 --address 0.0.0.0

INSTALL_K3S_SKIP_DOWNLOAD=true K3S_URL="https://10.1.1.2:6443" K3S_TOKEN_FILE="/etc/rancher/k3s/cluster-token" /tmp/install.sh

### IF ANY ISSUE CLEAN THE CLUSTER
sudo rm -rf /var/lib/rancher/k3s/server/db/etcd
```

### 8. Instalacja Cilium

```bash

# 1. Pobranie archiwum Helma dla Linux ARM64
curl -Lo /tmp/helm.tar.gz https://get.helm.sh/helm-v3.17.3-linux-arm64.tar.gz

# 2. Rozpakowanie archiwum w katalogu /tmp
tar -zxvf /tmp/helm.tar.gz -C /tmp/

# 3. Przeniesienie binaru helma do katalogu systemowego (wymaga sudo)
sudo mv /tmp/linux-arm64/helm /usr/local/bin/helm

# 4. Czyszczenie pobranych śmieci z /tmp
rm -rf /tmp/helm.tar.gz /tmp/linux-arm64

# W VM:
# 1. Wskazanie konfiguracji K3s dla Helma
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# 2. Dodanie oficjalnego repozytorium Cilium do Helma
helm repo add cilium https://helm.cilium.io/
helm repo update

# 3. Instalacja Cilium z Twoimi parametrami (z poprawionym IP na 10.1.1.5)
helm install cilium cilium/cilium --version 1.17.3 --namespace kube-system \
  --set kubeProxyReplacement=true \
  --set k8sServiceHost=10.1.1.2 \
  --set k8sServicePort=6443 \
  --set routingMode=tunnel \
  --set tunnelProtocol=vxlan \
  --set bpf.masquerade=true \
  --set hubble.enabled=true \
  --set hubble.relay.enabled=true \
  --set hubble.ui.enabled=true \
  --set operator.replicas=1 \
  --set ipam.operator.clusterPoolIPv4PodCIDRList=10.42.0.0/16


  sudo kubectl get pods -n kube-system
  sudo kubectl get nodes




```
## STATUS CHECK
```bash

sudo kubectl get pods -n kube-system
  sudo kubectl get nodes
NAME                               READY   STATUS              RESTARTS   AGE
cilium-envoy-q5mwx                 1/1     Running             0          46s
cilium-operator-7f965b8d5b-m45bq   1/1     Running             0          46s
cilium-plwnh                       1/1     Running             0          46s
coredns-695cbbfcb9-pc6g2           0/1     ContainerCreating   0          56s
hubble-relay-bb46f79d4-q4gps       0/1     ContainerCreating   0          46s
hubble-ui-5f65bfb688-ptc8b         0/2     ContainerCreating   0          46s
metrics-server-c8774f4f4-l5fd4     0/1     ContainerCreating   0          56s
NAME             STATUS   ROLES                AGE   VERSION
lima-opvmkub05   Ready    control-plane,etcd   20h   v1.34.5+k3s1


    /¯¯\
 /¯¯\__/¯¯\    Cilium:             OK
 \__/¯¯\__/    Operator:           OK
 /¯¯\__/¯¯\    Envoy DaemonSet:    OK
 \__/¯¯\__/    Hubble Relay:       OK
    \__/       ClusterMesh:        disabled

DaemonSet              cilium                   Desired: 3, Ready: 3/3, Available: 3/3
DaemonSet              cilium-envoy             Desired: 3, Ready: 3/3, Available: 3/3
Deployment             cilium-operator          Desired: 1, Ready: 1/1, Available: 1/1
Deployment             hubble-relay             Desired: 1, Ready: 1/1, Available: 1/1
Deployment             hubble-ui                Desired: 1, Ready: 1/1, Available: 1/1
Containers:            cilium                   Running: 3
                       cilium-envoy             Running: 3
                       cilium-operator          Running: 1
                       clustermesh-apiserver
                       hubble-relay             Running: 1
                       hubble-ui                Running: 1
Cluster Pods:          12/12 managed by Cilium
Helm chart version:    1.17.3
Image versions         cilium             quay.io/cilium/cilium:v1.17.3@sha256:1782794aeac951af139315c10eff34050aa7579c12827ee9ec376bb719b82873: 3
                       cilium-envoy       quay.io/cilium/cilium-envoy:v1.32.5-1744305768-f9ddca7dcd91f7ca25a505560e655c47d3dec2cf@sha256:a01cadf7974409b5c5c92ace3d6afa298408468ca24cab1cb413c04f89d3d1f9: 3
                       cilium-operator    quay.io/cilium/operator-generic:v1.17.3@sha256:8bd38d0e97a955b2d725929d60df09d712fb62b60b930551a29abac2dd92e597: 1
                       hubble-relay       quay.io/cilium/hubble-relay:v1.17.3@sha256:f8674b5139111ac828a8818da7f2d344b4a5bfbaeb122c5dc9abed3e74000c55: 1
                       hubble-ui          quay.io/cilium/hubble-ui-backend:v0.13.2@sha256:a034b7e98e6ea796ed26df8f4e71f83fc16465a19d166eff67a03b822c0bfa15: 1
                       hubble-ui          quay.io/cilium/hubble-ui:v0.13.2@sha256:9e37c1296b802830834cc87342a9182ccbb71ffebb711971e849221bd9d59392: 1
```

---


## Bieżąca konfiguracja klastra

### Nodes (17 MAJ 2026, 18:03 CET)

```
alex@lima-OPVMKUB05:~$ sudo kubectl get nodes
NAME             STATUS   ROLES                AGE     VERSION
lima-opvmkub05   Ready    control-plane,etcd   21h     v1.34.5+k3s1
lima-opvmkub13   Ready    <none>               7m33s   v1.34.5+k3s1
lima-opvmkub21   Ready    <none>               74s     v1.34.5+k3s1
```

### Pods

```
alex@lima-OPVMKUB05:~$ sudo kubectl get pods -n kube-system
NAME                               READY   STATUS    RESTARTS        AGE
cilium-c2n7x                       1/1     Running   0               26m
cilium-envoy-q5mwx                 1/1     Running   0               60m
cilium-envoy-t6rr4                 1/1     Running   0               20m
cilium-envoy-xsmqn                 1/1     Running   0               26m
cilium-fhfrb                       1/1     Running   8 (8m51s ago)   20m
cilium-operator-7f965b8d5b-m45bq   1/1     Running   0               60m
cilium-plwnh                       1/1     Running   0               60m
coredns-695cbbfcb9-9glds           1/1     Running   0               95s
hubble-relay-bb46f79d4-lnh44       1/1     Running   0               84s
hubble-ui-5f65bfb688-fq4c5         2/2     Running   0               82s
metrics-server-c8774f4f4-dsc6d     1/1     Running   0               81s
```


---

## Wdrożenie platformy (14.03.2026)

### MetalLB v0.14.9

```bash
# 1. Wskazanie konfiguracji K3s dla Helma
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# 2. Dodanie oficjalnego repozytorium MetalLB
helm repo add metallb https://metallb.github.io/metallb
helm repo update

# 3. Instalacja MetalLB
helm install metallb metallb/metallb \
  --namespace metallb-system \
  --create-namespace

cat > /tmp/metallb-config.yaml << 'EOF'
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: loadbalancer-ip-pool
  namespace: metallb-system
spec:
  addresses:
  - 10.1.3.16-10.1.3.23
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: loadbalancer-l2-advertisement
  namespace: metallb-system
spec:
  ipAddressPools:
  - loadbalancer-ip-pool
EOF

kubectl apply -f /tmp/metallb-config.yaml

# TEST
kubectl create deployment nginx-test --image=nginx
kubectl expose deployment nginx-test --port=80 --type=LoadBalancer
kubectl get svc nginx-test -w


```

### ArgoCD (stable)

```bash
# 1. Wskazanie konfiguracji K3s
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# 2. Dodanie repozytorium Helm Argo
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

# 3. Instalacja Argo CD
helm install argocd argo/argo-cd \
  --namespace argocd \
  --create-namespace \
  --set server.service.type=LoadBalancer

# 4. Sprawdzenie podów
kubectl get pods -n argocd -w

# 5. Sprawdzenie zewnętrznego IP z MetalLB
kubectl get svc -n argocd argocd-server

# 6. Pobranie początkowego hasła admina
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d; echo

  
```

#### Jak wyciągnąć hasło do panelu Argo?

Argo CD podczas instalacji automatycznie generuje losowe, bezpieczne hasło dla głównego użytkownika o nazwie admin. Jest ono schowane w sekretach Kubernetesa.

Aby je odczytać i zdekodować, uruchom tę komendę na Masterze:

```bash
sudo kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```

### FIX

Skoro tradycyjny MetalLB odbija się od vSwitcha Limy, włączymy w Cilium funkcję, która sprawi, że interfejs sieciowy Ubuntu zacznie oficjalnie i legalnie nasłuchiwać na adresach z puli MetalLB.

Stwórzmy profil polityki L2 dla Cilium. Wklej to w całości na Masterze:

```bash
sudo cat > /tmp/cilium-l2-policy.yaml << 'EOF'
apiVersion: cilium.io/v2alpha1
kind: CiliumL2AnnouncementPolicy
metadata:
  name: cilium-l2-policy
  namespace: kube-system
spec:
  # Pozwól na rozgłaszanie usług typu LoadBalancer
  serviceSelector:
    matchExpressions:
      - key: somekey
        operator: DoesNotExist
  nodeSelector:
    matchExpressions:
      - key: kubernetes.io/os
        operator: In
        values:
          - linux
  interfaces:
    - ^lima.*
    - ^eth.*
    - ^en.*
---
apiVersion: cilium.io/v2alpha1
kind: CiliumLoadBalancerIPPool
metadata:
  name: cilium-ip-pool
  namespace: kube-system
spec:
  blocks:
    - cidr: 10.1.1.38/32
    - cidr: 10.1.1.39/32
EOF
```

Zaaplikuj konfigurację do klastra:

```bash
sudo kubectl apply -f /tmp/cilium-l2-policy.yaml
```

POTEM TO ZROBILEM

```bash
sudo kubectl delete -f /tmp/cilium-l2-policy.yaml
sudo kubectl delete -f /tmp/metallb-config.yaml
sudo kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "ClusterIP"}}'
sudo kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
```

### ArgoCD Applications (Helm-based)

| Aplikacja | Chart | Wersja | VIP | Status |
|-----------|-------|--------|-----|--------|
| cert-manager | jetstack/cert-manager | v1.17.1 | — | Synced/Healthy |
| traefik | traefik/traefik | 34.3.0 | 10.189.5.51 | Synced/Healthy |
| monitoring | prometheus-community/kube-prometheus-stack | 72.6.2 | Grafana: .54, Prometheus: .55 | Synced/Healthy |

---

### Longhorn v1.8.1 (via Helm, nie ArgoCD)

- ArgoCD pre-upgrade hook blokował na brakującym ServiceAccount (chicken-and-egg)
- Zainstalowano bezpośrednio: `helm install longhorn ... --no-hooks`
- 2 repliki per volume, Retain policy, default StorageClass
- Wymagało labeli: `kubectl label nodes --all node.longhorn.io/create-default-disk=true`
- 3 PVC (Grafana 10Gi, Prometheus 50Gi, Alertmanager 5Gi) — wszystkie Bound/Healthy

### Podsumowanie VIP

| Serwis | IP | Port |
|--------|----|------|
| ArgoCD | 10.189.5.50 | 443 |
| Traefik | 10.189.5.51 | 80, 443 |
| Grafana | 10.189.5.54 | 80 |
| Prometheus | 10.189.5.55 | 9090 |

### Pod count (61 podów)

- longhorn-system: 26
- kube-system: 11
- monitoring: 8
- argocd: 7
- metallb-system: 4
- cert-manager: 3
- traefik: 2

---

## Kolejne kroki

1. **Git repo** — utworzyć `ZSEL-OPOLE/gitops-infra` i podpiąć app-of-apps
2. **Ollama bridge** — ExternalName/Endpoints w K8s → natywne Ollama na Mac hostach
3. **Open WebUI** — deployment + IngressRoute na Traefik
4. **Monitoring extras** — SNMP exporter (MikroTik), Blackbox exporter, Pushgateway
5. **IngressRoutes** — Traefik routes dla ArgoCD, Grafana, Longhorn UI, Open WebUI



---

## Znane problemy i obejścia

### 1. Internet w VM przez bridged jest ekstremalnie powolny

**Problem**: Download przez en1 (bridged/socket_vmnet) — ~1 KB/s.
**Przyczyna**: socket_vmnet routuje ruch w userspace, traffic shape na macOS level.
**Obejście**: Zawsze pobieraj duże pliki na hoście i kopiuj do VM chyba ze nie ma problemu.


### 2. K3s v1.34.5 — zabrania label `node-role.kubernetes.io/*` w kubelet

**Problem**: `--node-labels` z `node-role.kubernetes.io/control-plane` powoduje crash loop.
**Błąd**: `unknown 'kubernetes.io' or 'k8s.io' labels specified with --node-labels`
**Rozwiązanie**: Nie ustawiaj tych labeli w config.yaml. K3s sam nadaje je po rejestracji.

### 3. Zmiana node-ip wymaga resetu etcd

**Problem**: Jeśli klaster był już zbootstrapowany z innym IP, zmiana `node-ip` w config.yaml
powoduje niezgodność z etcd member list.
**Rozwiązanie**: Jednorazowe:
```bash
systemctl stop k3s
rm -rf /var/lib/rancher/k3s/server/db/etcd
systemctl start k3s
```
> **⚠️ Uwaga**: To kasuje cały stan klastra! Akceptowalne tylko przy świeżej instalacji.

### 4. socket_vmnet — ścieżka nie może zawierać symlinków

**Problem**: Lima waliduje że ścieżka do socket_vmnet jest "root-owned" na każdym segmencie
i nie zawiera symlinków. `/opt/homebrew/opt/socket_vmnet` jest symlinkiem.
**Rozwiązanie**: Użyj pełnej ścieżki Cellar:
```yaml
socketVMNet: "/opt/homebrew/Cellar/socket_vmnet/1.2.2/bin/socket_vmnet"
```

### 5. Homebrew permissions po socket_vmnet

**Problem**: `sudo brew services start socket_vmnet` zmienia ownership na root:admin.
Następne brew operations mogą wymagać:
```bash
sudo chown -R admin /opt/homebrew    # przywraca normalny dostęp
```


## Kluczowa lekcja

> **Lima na macOS NIE NADAJE SIĘ do Kubernetes overlay networking w trybie vzNAT.**
>
> Tryb vzNAT (domyślny w Lima 2.x z VZ framework) daje VM prywatny adres IP za NAT.
> Port forwarding obsługuje TCP dobrze, ale UDP (wymagany przez VXLAN/Geneve/WireGuard)
> przechodzi przez userspace proxy, który przepisuje adresy źródłowe. To łamie
> encapsulację overlay i powoduje silent failures — klaster wygląda zdrowo (`kubectl get nodes`
> → Ready), ale cross-node pod communication nie działa.
>
> **Jedyne poprawne rozwiązanie**: bridged networking przez `socket_vmnet`, który daje VM
> bezpośredni dostęp L2 do fizycznej sieci. VM-ki widzą się nawzajem tak jakby były
> fizycznymi maszynami w tej samej sieci.

---
