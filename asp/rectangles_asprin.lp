#const nrect = 1.
#const selectcount = 2.
#const overlapprio = 3.
#const impurityprio = 2.
#const outlierprio = 1.

rectangle(1..nrect).

pointid(I) :- value(I,A,V).
attribute(A) :- value(I, A, V).
cluster(CL) :- cluster(I,CL).

selectcount { selattr(A):attribute(A), not target(A) } selectcount.

2 { rectval(R,A,V) : value(_,A,V) } 2 :- rectangle(R), selattr(A).

attrinlier(R,I,A) :- value(I,A,V), rectval(R,A,V0), rectval(R,A,V1), V >= V0, V <= V1, V0 < V1.
attroutlier(R,I,A) :- value(I,A,V), rectval(R,A,V0), rectval(R,A,V1), V < V0, V0 < V1.
attroutlier(R,I,A) :- value(I,A,V), rectval(R,A,V0), rectval(R,A,V1), V > V1, V0 < V1.

rectoutlier(R, I) :- attroutlier(R,I,A).
rectinlier(R, I) :- attrinlier(R,I,A), not rectoutlier(R,I).

rectinliercount(R,C) :- rectangle(R), C=#count{ I : rectinlier(R,I) }.

inlier(I) :- rectinlier(R, I).
outlier(I) :- pointid(I), not inlier(I).

% An overlapping point is a single point that belongs to two rectangles
overlappoint(I, R1, R2) :- rectinlier(R1, I), rectinlier(R2, I), R1 < R2.

impure(R) :- rectangle(R), rectinlier(R,I1), rectinlier(R,I2), I1 < I2,
                cluster(I1, C1), cluster(I2, C2), C1 != C2.

% Given an impure rectangle and a cluster, how many points are not of that cluster
impurity(R,CL1,IC) :- impure(R), cluster(CL1), 
            IC=#count{ I: cluster(I, CL2), CL2 != CL1, rectinlier(R,I) }.
% The minimal number of impurity determines the purest cluster of a rectangle
impurity(R,M) :- impure(R), M=#min{ CLI : impurity(R,CL,CLI)}.

rectcluster(R, CL) :- rectangle(R), not impure(R), rectinlier(R,I), cluster(I, CL).
rectcluster(R, CL) :- impure(R), impurity(R,IM), impurity(R,CL,IM).

impurepoint(I) :- rectinlier(R,I), impure(R), cluster(I,CLI), rectcluster(R,CLR), CLI != CLR.

minrectval(R,A,V0,V1) :- rectangle(R), selattr(A), V0=#min{ V : rectinlier(R,I), value(I,A,V) },
                            V1=#max{ V : rectinlier(R,I), value(I,A,V) }.

:- rectangle(R), not rectinlier(R, _).
:- rectangle(R), rectcluster(R,CL1), rectcluster(R,CL2), CL1 != CL2.

outliercount(C) :- C=#count{ I : outlier(I) }.
overlapcount(C) :- C=#count{ I : overlappoint(I, R1, R2) }.
impurecount(C) :- C=#count{ I : impurepoint(I) }.


#preference(overlap, less(cardinality)){
    overlappoint(I, R1, R2) : rectangle(R1), rectangle(R2), pointid(I)
}.
#preference(impurity, less(cardinality)){
    impurepoint(I): pointid(I)
}.
#preference(outlier, less(cardinality)){
    outlier(I) : pointid(I)
}.
#preference(all, lexico){
    overlapprio::**overlap; impurityprio::**impurity; outlierprio::**outlier
}.

#optimize(all).

#show minrectval/4.
#show rectinliercount/2.
#show rectcluster/2.
#show outliercount/1.
#show overlapcount/1.
#show impurecount/1.
#show selattr/1.
