---
title: "Network Configuration — MikroTik CRS354"
subtitle: "Network Infrastructure Documentation — Kubernetes Cluster"
author:
  - "Alex"
  - "Michał"
date: "2026-04-25"
subject: "Network Team"
keywords: [MikroTik, Kubernetes, LACP, CRS354, network]
---

\newpage

## Changelog

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-11 | Alex, Michał | Initial version — CRS317-1G-16S+, 10G SFP+ LACP topology |
| 1.1 | 2026-04-11 | Michał | Detailed port assignment, topology diagram |
| 1.2 | 2026-04-11 | Michał | Added CONFIG.rsc data, bridge-wan configuration |
| 2.0 | 2026-04-11 | Alex | Switch replaced with CRS354-48G-4S+2Q+RM — 1G RJ45 ports (SFP+ instability at 80°C) |
| 2.1 | 2026-04-11 | Michał | Config update: node ports in bonds, management configuration |
| 2.2 | 2026-04-11 | Alex, Michał | Simplified notes section, removed threat table |
| 3.0 | 2026-04-11 | Alex, Michał | Updated from RouterOS 7.18.2 export — second uplink ether48, ether11/12 in bridge |
| 3.1 | 2026-04-11 | Alex, Michał | Distribution panel PD1 ports (ether9, 11–12, 21–24) |
| 3.2 | 2026-04-11 | Alex, Michał | MAC addresses for all assigned ports, QSFP+ sub-lanes, ether49 |
| 3.3 | 2026-04-11 | Alex, Michał | Review: port layout, bridge MAC, sfp-sfpplus1, inferred MACs |
| 3.4 | 2026-04-11 | Alex, Michał | Translated to English |
| 3.5 | 2026-04-11 | Michał | Renamed nodes: Apple Mac M4 → Apple Mac Pro |
| 3.6 | 2026-04-11 | Michał | Removed physical port layout diagram from topology |
| 3.7 | 2026-04-12 | Alex, Michał | Applied node naming convention: Node 1–4 → OPHWNODE01–04 |
| 3.8 | 2026-04-12 | Alex, Michał | Added Mac bond interface names (LINK-NODE1–4-AGG) to nodes table |
| 3.9 | 2026-04-12 | Alex, Michał | Added gateway and DNS info to nodes section |
| 4.0 | 2026-04-12 | Alex, Michał | Added VM section: 24x OPVMKUB01–24 (Lima), IP ranges per node |
| 4.1 | 2026-04-12 | Alex, Michał | New addressing: 10.1.255.0/24, nodes .201–.204 |
| 4.2 | 2026-04-12 | Alex, Michał | VM network changed to 10.1.1.0/24, IPs .1–.24 sequential |
| 4.3 | 2026-04-12 | Alex, Michał | DNS on switch: 10.1.53.53, static records for all hosts |
| 4.4 | 2026-04-12 | Alex, Michał | DNS records changed from .local to .internal — no client config required |
| 4.5 | 2026-04-25 | Alex, Michał | Added PD1 ports: ether33–36 (PD1/110–113), ether43–46 (PD1/114–117) |

\newpage

### Device

- **Model:** CRS354-48G-4S+2Q+RM
- **Serial:** HK60AM6CECJ
- **RouterOS:** 7.18.2
- **Software ID:** WFM1-CBPK

### Nodes — Apple Mac Pro

- 4x Apple Mac Pro
- Each node: 2x 1Gbps RJ45 in LACP (2Gbps per node)
- Network: 10.1.255.0/24
- Gateway: `10.1.0.1` (reachable via ether48 — WAN-ETH)
- DNS: `10.1.53.53`

| Node | IP | MAC (bond) | Bond interface |
|------|----|------------|----------------|
| OPHWNODE01 | `10.1.255.201` | `60:d0:39:ad:57:9f` | LINK-NODE1-AGG |
| OPHWNODE02 | `10.1.255.202` | `60:d0:39:a0:a7:e2` | LINK-NODE2-AGG |
| OPHWNODE03 | `10.1.255.203` | `60:d0:39:af:23:6a` | LINK-NODE3-AGG |
| OPHWNODE04 | `10.1.255.204` | `60:d0:39:a2:4e:34` | LINK-NODE4-AGG |

### VMs — Kubernetes (Lima)

- 6x VM per node, 24x total
- Type: Lima (Apple Virtualization Framework — `vmType: vz`)
- OS: Ubuntu 24.04 Server ARM64
- CPU: 10 vCPU, RAM: 24 GiB, Disk: 800 GiB
- Network: bridged on `LINK-NODEx-AGG` (per host)
- Network: 10.1.1.0/24

| VM | Host | IP |
|----|------|----|
| OPVMKUB01 | OPHWNODE01 | `10.1.1.1` |
| OPVMKUB02 | OPHWNODE01 | `10.1.1.2` |
| OPVMKUB03 | OPHWNODE01 | `10.1.1.3` |
| OPVMKUB04 | OPHWNODE01 | `10.1.1.4` |
| OPVMKUB05 | OPHWNODE01 | `10.1.1.5` |
| OPVMKUB06 | OPHWNODE01 | `10.1.1.6` |
| OPVMKUB07 | OPHWNODE02 | `10.1.1.7` |
| OPVMKUB08 | OPHWNODE02 | `10.1.1.8` |
| OPVMKUB09 | OPHWNODE02 | `10.1.1.9` |
| OPVMKUB10 | OPHWNODE02 | `10.1.1.10` |
| OPVMKUB11 | OPHWNODE02 | `10.1.1.11` |
| OPVMKUB12 | OPHWNODE02 | `10.1.1.12` |
| OPVMKUB13 | OPHWNODE03 | `10.1.1.13` |
| OPVMKUB14 | OPHWNODE03 | `10.1.1.14` |
| OPVMKUB15 | OPHWNODE03 | `10.1.1.15` |
| OPVMKUB16 | OPHWNODE03 | `10.1.1.16` |
| OPVMKUB17 | OPHWNODE03 | `10.1.1.17` |
| OPVMKUB18 | OPHWNODE03 | `10.1.1.18` |
| OPVMKUB19 | OPHWNODE04 | `10.1.1.19` |
| OPVMKUB20 | OPHWNODE04 | `10.1.1.20` |
| OPVMKUB21 | OPHWNODE04 | `10.1.1.21` |
| OPVMKUB22 | OPHWNODE04 | `10.1.1.22` |
| OPVMKUB23 | OPHWNODE04 | `10.1.1.23` |
| OPVMKUB24 | OPHWNODE04 | `10.1.1.24` |

### Switch — MikroTik CRS354-48G-4S+2Q+RM

- 48x Gigabit Ethernet RJ45 (ether1–48, switch1)
- 1x GE (ether49, switch2)
- 4x SFP+ 10Gbps (sfp-sfpplus1–4)
- 2x QSFP+ 40Gbps, each split into 4x 10G sub-lanes (qsfpplus1-1..4, qsfpplus2-1..4)
- 1U rack

#### Port Assignment

**Bridge — bridge-wan**

| Interface | MAC | Usage | Active |
|-----------|-----|-------|--------|
| sfp-sfpplus1 | `04:F4:1C:8F:76:9C` | FO uplink — WAN-FIBRE | no |
| ether48 | `04:F4:1C:8F:76:CF` | Copper uplink — WAN-ETH | yes |
| bond1 | `04:F4:1C:8F:76:A0` | OPHWNODE01 | yes |
| bond2 | `04:F4:1C:8F:76:A1` | OPHWNODE02 | yes |
| bond3 | `04:F4:1C:8F:76:B8` | OPHWNODE03 | yes |
| bond4 | `04:F4:1C:8F:76:B9` | OPHWNODE04 | yes |
| ether9 | `04:F4:1C:8F:76:A8` | PD1/124 | yes |
| ether11 | `04:F4:1C:8F:76:AA` | PD1/122 | yes |
| ether12 | `04:F4:1C:8F:76:AB` | PD1/123 | yes |
| ether21 | `04:F4:1C:8F:76:B4` | PD1/120 | yes |
| ether22 | `04:F4:1C:8F:76:B5` | PD1/121 | yes |
| ether23 | `04:F4:1C:8F:76:B6` | PD1/119 | yes |
| ether24 | `04:F4:1C:8F:76:B7` | PD1/118 | yes |
| ether33 | `04:F4:1C:8F:76:C0` | PD1/110 | yes |
| ether34 | `04:F4:1C:8F:76:C1` | PD1/111 | yes |
| ether35 | `04:F4:1C:8F:76:C2` | PD1/112 | yes |
| ether36 | `04:F4:1C:8F:76:C3` | PD1/113 | yes |
| ether43 | `04:F4:1C:8F:76:CA` | PD1/114 | yes |
| ether44 | `04:F4:1C:8F:76:CB` | PD1/115 | yes |
| ether45 | `04:F4:1C:8F:76:CC` | PD1/116 | yes |
| ether46 | `04:F4:1C:8F:76:CD` | PD1/117 | yes |

**Bonds — slave ports**

| Bond | Port | MAC |
|------|------|-----|
| bond1 | ether1 | `04:F4:1C:8F:76:A0` |
| bond1 | ether13 | `04:F4:1C:8F:76:AC` |
| bond2 | ether2 | `04:F4:1C:8F:76:A1` |
| bond2 | ether14 | `04:F4:1C:8F:76:AD` |
| bond3 | ether25 | `04:F4:1C:8F:76:B8` |
| bond3 | ether37 | `04:F4:1C:8F:76:C4` |
| bond4 | ether26 | `04:F4:1C:8F:76:B9` |
| bond4 | ether38 | `04:F4:1C:8F:76:C5` |

#### Topology

```
        Upstream network
               |
           ether48 (WAN-ETH)
               |
           bridge-wan (L2)
      /      |       |       |
  bond1   bond2   bond3   bond4
 (1+13) (2+14) (25+37) (26+38)
   |       |       |       |
 OPHWNODE01  OPHWNODE02  OPHWNODE03  OPHWNODE04
```

Each bond's ports are 6 physical positions apart (12 port numbers) in the same row — intentionally distributed across separate switch processors (ASICs), providing LACP resilience against single-block failure.

#### LACP Configuration (802.3ad)

| Bond | Ports | Node | Hash policy |
|------|-------|------|-------------|
| bond1 | ether1 + ether13 | OPHWNODE01 | layer-2-and-3 |
| bond2 | ether2 + ether14 | OPHWNODE02 | layer-2-and-3 |
| bond3 | ether25 + ether37 | OPHWNODE03 | layer-2-and-3 |
| bond4 | ether26 + ether38 | OPHWNODE04 | layer-2-and-3 |

- Throughput per node: 2x 1Gbps = 2Gbps
- Total node throughput: 4x 2Gbps = 8Gbps

#### Comparison with Previous Switch (CRS317)

CRS317 replaced due to SFP+ transceiver instability and overheating to ~80°C.

| | CRS317-1G-16S+ | CRS354-48G-4S+2Q+RM |
|-|----------------|----------------------|
| Node ports | 10G SFP+ | 1G RJ45 |
| Throughput per node | 20Gbps | 2Gbps |
| Total node throughput | 80Gbps | 8Gbps |
| Stability | SFP+ issues (80°C) | Stable copper links |
| Free ports | 7x SFP+ | 23x RJ45 + 4x SFP+ + 2x QSFP+ |

#### Management Configuration

- IP: `10.1.53.53/16` (bridge-wan)
- Telnet: disabled
- WWW (HTTP): disabled
- Neighbor discovery: disabled on dynamic interfaces
- Timezone: Europe/Warsaw
- Recommended access: Winbox

#### DNS

- Address: `10.1.53.53` (UDP/TCP 53)
- Upstream: `8.8.8.8`, `1.1.1.1`
- Default route: `10.1.0.1`
- Static records:

| Name | IP |
|------|----|
| ophwnode01, ophwnode01.internal | `10.1.255.201` |
| ophwnode02, ophwnode02.internal | `10.1.255.202` |
| ophwnode03, ophwnode03.internal | `10.1.255.203` |
| ophwnode04, ophwnode04.internal | `10.1.255.204` |
| opvmkub01–opvmkub24 | `10.1.1.1–10.1.1.24` |
| opvmkub01.internal–opvmkub24.internal | `10.1.1.1–10.1.1.24` |

#### High Availability (HA)

Cable-level redundancy is provided — each node is connected via two physical links in LACP (802.3ad). Failure of a single cable or port does not interrupt connectivity.

Switch-level redundancy **is not provided** — the entire infrastructure relies on a single CRS354 device. Switch failure results in loss of connectivity for the entire cluster.

#### Notes

Apple Mac Pro has built-in 10GbE — the switch limits connections to 1G. Returning to 10G requires stable SFP+ transceivers or a switch with native 10G RJ45 ports.
