#const maxrange = 100.
#const nrect = 3.

parameter(x;y;z;t).
value(0..maxrange).
rectangle(1..nrect).

2 { range(R, P, V) : value(V) } 2 :- rectangle(R), parameter(P).

part_overlap(R1, R2, P) :- range(R1, P, V10), range(R1, P, V11), 
                        range(R2, P, V20), range(R2, P, V21),
                        V10 < V11, V20 < V21,
                        V20 >= V10, V20 < V11.

paramoverlap(R1, R2, P) :- part_overlap(R1, R2, P), 
                        range(R1, P, V10), range(R1, P, V11), 
                        range(R2, P, V20), range(R2, P, V21),
                        V10 < V11, V20 < V21,
                        V21 >= V11.

paramoverlap(R1, R2, P) :- part_overlap(R1, R2, P), 
                        range(R1, P, V10), range(R1, P, V11), 
                        range(R2, P, V20), range(R2, P, V21),
                        V10 < V11, V20 < V21,
                        V21 <= V11.

#show paramoverlap/3.