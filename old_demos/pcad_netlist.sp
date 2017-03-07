.temp 110.0
.include "d.inc"
.hdl "powerMOSVA.va"
.print TRAN I(V1) I(V2) V(N003, N007)


L2 N002 N003 100n IC=0.001 

*Gate impedances
L1 N004 N0099 12.0n 
R9 N0099 N006 5
L12 N004 N00992 12.0n 
R92 N00992 N0062 5


 *  D    G    S
X1 N003 N006 N007 powerMOSVA
X2 N003 N0062 N007 powerMOSVA
* Load
R1 N001 N002 10
D1 N007 N003 diode1
D2 N007 N003 diode1
V1 N001 0 400
V2 N004 N008  0 PULSE(-5 20 0 10n 10n 10u 20u) 
L3 N007 N008 12.0n
L4 N008 0 5n

.tran 5e-9 70e-6 UIC

.end