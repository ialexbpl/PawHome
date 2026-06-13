# 2026-04-25 10:41:24 by RouterOS 7.18.2
# software id = WFM1-CBPK
#
# model = CRS354-48G-4S+2Q+
# serial number = HK60AM6CECJ
/interface bridge
add name=bridge-wan
/interface ethernet
set [ find default-name=ether1 ] auto-negotiation=no comment=Node1-P1
set [ find default-name=ether2 ] auto-negotiation=no comment=Node2-P1
set [ find default-name=ether9 ] comment=PD1/124
set [ find default-name=ether11 ] comment=PD1/122
set [ find default-name=ether12 ] comment=PD1/123
set [ find default-name=ether13 ] auto-negotiation=no comment=Node1-P2
set [ find default-name=ether14 ] auto-negotiation=no comment=Node2-P2
set [ find default-name=ether21 ] comment=PD1/120
set [ find default-name=ether22 ] comment=PD1/121
set [ find default-name=ether23 ] comment=PD1/119
set [ find default-name=ether24 ] comment=PD1/118
set [ find default-name=ether25 ] auto-negotiation=no comment=Node3-P1
set [ find default-name=ether26 ] auto-negotiation=no comment=Node4-P1
set [ find default-name=ether33 ] comment=PD1/110
set [ find default-name=ether34 ] comment=PD1/111
set [ find default-name=ether35 ] comment=PD1/112
set [ find default-name=ether36 ] comment=PD1/113
set [ find default-name=ether37 ] auto-negotiation=no comment=Node3-P2
set [ find default-name=ether38 ] auto-negotiation=no comment=Node4-P2
set [ find default-name=ether43 ] comment=PD1/114
set [ find default-name=ether44 ] comment=PD1/115
set [ find default-name=ether45 ] comment=PD1/116
set [ find default-name=ether46 ] comment=PD1/117
set [ find default-name=ether48 ] comment=WAN-ETH
set [ find default-name=sfp-sfpplus1 ] comment=WAN-FIBRE
/interface bonding
add mode=802.3ad name=bond1 slaves=ether1,ether13 transmit-hash-policy=\
    layer-2-and-3
add mode=802.3ad name=bond2 slaves=ether2,ether14 transmit-hash-policy=\
    layer-2-and-3
add mode=802.3ad name=bond3 slaves=ether25,ether37 transmit-hash-policy=\
    layer-2-and-3
add mode=802.3ad name=bond4 slaves=ether26,ether38 transmit-hash-policy=\
    layer-2-and-3
/port
set 0 name=serial0
/interface bridge port
add bridge=bridge-wan interface=sfp-sfpplus1
add bridge=bridge-wan interface=bond1
add bridge=bridge-wan interface=bond2
add bridge=bridge-wan interface=bond3
add bridge=bridge-wan interface=bond4
add bridge=bridge-wan interface=ether12
add bridge=bridge-wan interface=ether11
add bridge=bridge-wan interface=ether48
add bridge=bridge-wan interface=ether23
add bridge=bridge-wan interface=ether24
add bridge=bridge-wan interface=ether9
add bridge=bridge-wan interface=ether22
add bridge=bridge-wan interface=ether21
add bridge=bridge-wan interface=ether33
add bridge=bridge-wan interface=ether34
add bridge=bridge-wan interface=ether35
add bridge=bridge-wan interface=ether36
add bridge=bridge-wan interface=ether43
add bridge=bridge-wan interface=ether44
add bridge=bridge-wan interface=ether45
add bridge=bridge-wan interface=ether46
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/ip address
add address=10.1.53.53/16 interface=bridge-wan network=10.1.0.0
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,1.1.1.1
/ip dns static
add address=10.1.255.201 name=ophwnode01 type=A
add address=10.1.255.202 name=ophwnode02 type=A
add address=10.1.255.203 name=ophwnode03 type=A
add address=10.1.255.204 name=ophwnode04 type=A
add address=10.1.1.1 name=opvmkub01 type=A
add address=10.1.1.2 name=opvmkub02 type=A
add address=10.1.1.3 name=opvmkub03 type=A
add address=10.1.1.4 name=opvmkub04 type=A
add address=10.1.1.5 name=opvmkub05 type=A
add address=10.1.1.6 name=opvmkub06 type=A
add address=10.1.1.7 name=opvmkub07 type=A
add address=10.1.1.8 name=opvmkub08 type=A
add address=10.1.1.9 name=opvmkub09 type=A
add address=10.1.1.10 name=opvmkub10 type=A
add address=10.1.1.11 name=opvmkub11 type=A
add address=10.1.1.12 name=opvmkub12 type=A
add address=10.1.1.13 name=opvmkub13 type=A
add address=10.1.1.14 name=opvmkub14 type=A
add address=10.1.1.15 name=opvmkub15 type=A
add address=10.1.1.16 name=opvmkub16 type=A
add address=10.1.1.17 name=opvmkub17 type=A
add address=10.1.1.18 name=opvmkub18 type=A
add address=10.1.1.19 name=opvmkub19 type=A
add address=10.1.1.20 name=opvmkub20 type=A
add address=10.1.1.21 name=opvmkub21 type=A
add address=10.1.1.22 name=opvmkub22 type=A
add address=10.1.1.23 name=opvmkub23 type=A
add address=10.1.1.24 name=opvmkub24 type=A
add address=10.1.255.201 name=ophwnode01.internal type=A
add address=10.1.255.202 name=ophwnode02.internal type=A
add address=10.1.255.203 name=ophwnode03.internal type=A
add address=10.1.255.204 name=ophwnode04.internal type=A
add address=10.1.1.1 name=opvmkub01.internal type=A
add address=10.1.1.2 name=opvmkub02.internal type=A
add address=10.1.1.3 name=opvmkub03.internal type=A
add address=10.1.1.4 name=opvmkub04.internal type=A
add address=10.1.1.5 name=opvmkub05.internal type=A
add address=10.1.1.6 name=opvmkub06.internal type=A
add address=10.1.1.7 name=opvmkub07.internal type=A
add address=10.1.1.8 name=opvmkub08.internal type=A
add address=10.1.1.9 name=opvmkub09.internal type=A
add address=10.1.1.10 name=opvmkub10.internal type=A
add address=10.1.1.11 name=opvmkub11.internal type=A
add address=10.1.1.12 name=opvmkub12.internal type=A
add address=10.1.1.13 name=opvmkub13.internal type=A
add address=10.1.1.14 name=opvmkub14.internal type=A
add address=10.1.1.15 name=opvmkub15.internal type=A
add address=10.1.1.16 name=opvmkub16.internal type=A
add address=10.1.1.17 name=opvmkub17.internal type=A
add address=10.1.1.18 name=opvmkub18.internal type=A
add address=10.1.1.19 name=opvmkub19.internal type=A
add address=10.1.1.20 name=opvmkub20.internal type=A
add address=10.1.1.21 name=opvmkub21.internal type=A
add address=10.1.1.22 name=opvmkub22.internal type=A
add address=10.1.1.23 name=opvmkub23.internal type=A
add address=10.1.1.24 name=opvmkub24.internal type=A
/ip route
add gateway=10.1.0.1
/ip service
set telnet disabled=yes
set www disabled=yes
/system clock
set time-zone-name=Europe/Warsaw
/system note
set show-at-login=no
/system routerboard settings
set enter-setup-on=delete-key
