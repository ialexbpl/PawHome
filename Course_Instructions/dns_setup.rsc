/ip address
add address=10.1.53.53/16 interface=bridge-wan
/ip route
add gateway=10.1.0.1
/ip dns
set servers=8.8.8.8,1.1.1.1 allow-remote-requests=yes
/ip dns static
add name=ophwnode01.internal address=10.1.255.201 ttl=1d
add name=ophwnode02.internal address=10.1.255.202 ttl=1d
add name=ophwnode03.internal address=10.1.255.203 ttl=1d
add name=ophwnode04.internal address=10.1.255.204 ttl=1d
add name=opvmkub01.internal address=10.1.1.1 ttl=1d
add name=opvmkub02.internal address=10.1.1.2 ttl=1d
add name=opvmkub03.internal address=10.1.1.3 ttl=1d
add name=opvmkub04.internal address=10.1.1.4 ttl=1d
add name=opvmkub05.internal address=10.1.1.5 ttl=1d
add name=opvmkub06.internal address=10.1.1.6 ttl=1d
add name=opvmkub07.internal address=10.1.1.7 ttl=1d
add name=opvmkub08.internal address=10.1.1.8 ttl=1d
add name=opvmkub09.internal address=10.1.1.9 ttl=1d
add name=opvmkub10.internal address=10.1.1.10 ttl=1d
add name=opvmkub11.internal address=10.1.1.11 ttl=1d
add name=opvmkub12.internal address=10.1.1.12 ttl=1d
add name=opvmkub13.internal address=10.1.1.13 ttl=1d
add name=opvmkub14.internal address=10.1.1.14 ttl=1d
add name=opvmkub15.internal address=10.1.1.15 ttl=1d
add name=opvmkub16.internal address=10.1.1.16 ttl=1d
add name=opvmkub17.internal address=10.1.1.17 ttl=1d
add name=opvmkub18.internal address=10.1.1.18 ttl=1d
add name=opvmkub19.internal address=10.1.1.19 ttl=1d
add name=opvmkub20.internal address=10.1.1.20 ttl=1d
add name=opvmkub21.internal address=10.1.1.21 ttl=1d
add name=opvmkub22.internal address=10.1.1.22 ttl=1d
add name=opvmkub23.internal address=10.1.1.23 ttl=1d
add name=opvmkub24.internal address=10.1.1.24 ttl=1d
