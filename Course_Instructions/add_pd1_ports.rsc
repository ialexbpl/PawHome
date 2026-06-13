/interface ethernet
set [ find default-name=ether33 ] comment=PD1/110
set [ find default-name=ether34 ] comment=PD1/111
set [ find default-name=ether35 ] comment=PD1/112
set [ find default-name=ether36 ] comment=PD1/113
set [ find default-name=ether43 ] comment=PD1/114
set [ find default-name=ether44 ] comment=PD1/115
set [ find default-name=ether45 ] comment=PD1/116
set [ find default-name=ether46 ] comment=PD1/117
/interface bridge port
add bridge=bridge-wan interface=ether33
add bridge=bridge-wan interface=ether34
add bridge=bridge-wan interface=ether35
add bridge=bridge-wan interface=ether36
add bridge=bridge-wan interface=ether43
add bridge=bridge-wan interface=ether44
add bridge=bridge-wan interface=ether45
add bridge=bridge-wan interface=ether46
