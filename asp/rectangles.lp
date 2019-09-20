#const nrect = 1.
#const selectcount = 2.

rectangle(1..nrect).

pointid(I) :- value(I,A,V).
attribute(A) :- value(I, A, V).
cluster(CL) :- cluster(I,CL).

selectcount { selattr(A):attribute(A) } selectcount.

2 { rectval(R,A,V) : value(_,A,V) } 2 :- rectangle(R), selattr(A).

attrinlier(R,I,A) :- value(I,A,V), rectval(R,A,V0), rectval(R,A,V1), V >= V0, V <= V1, V0 < V1.
attroutlier(R,I,A) :- value(I,A,V), rectval(R,A,V0), rectval(R,A,V1), V < V0, V0 < V1.
attroutlier(R,I,A) :- value(I,A,V), rectval(R,A,V0), rectval(R,A,V1), V > V1, V0 < V1.

rectoutlier(R, I) :- attroutlier(R,I,A).
rectinlier(R, I) :- attrinlier(R,I,A), not rectoutlier(R,I).

rectinliercount(R,C) :- rectangle(R), C=#count{ I : rectinlier(R,I) }.

inlier(I) :- rectinlier(R, I).
outlier(I) :- pointid(I), not inlier(I).

outliercount(C) :- C=#count{ I : outlier(I) }.

overlaps(R1, R2) :- rectinlier(R1, I), rectinlier(R2, I), R1 < R2.
overlapcount(C) :- overlaps(R1, R2), C=#count{ I : rectinlier(R1, I), rectinlier(R2, I) }.
overlapcount(0) :- rectangle(R1), rectangle(R2), not overlaps(R1,R2).

impure(R) :- rectangle(R), rectinlier(R,I1), rectinlier(R,I2), I1 < I2,
                cluster(I1, C1), cluster(I2, C2), C1 != C2.

% Given an impure rectangle and a cluster, how many points are not of that cluster
impurity(R,CL1,IC) :- impure(R), cluster(CL1), IC=#count{ I: cluster(I, CL2), CL2 != CL1 }.


minrectval(R,A,V0,V1) :- rectangle(R), selattr(A), V0=#min{ V : rectinlier(R,I), value(I,A,V) },
                            V1=#max{ V : rectinlier(R,I), value(I,A,V) }.

:- rectangle(R), not rectinlier(R, _).
%:- overlaps(R1, R2).
%:- outlier(I).
%:- impure(R).

#minimize{ OU: overlapcount(OU) }.
#minimize{ OV: outliercount(OV) }.
#minimize{ IM: impurity(R,CL,IM)}.

#show minrectval/4.
#show selattr/1.
#show overlapcount/1.
#show outliercount/1.
#show impurity/3.