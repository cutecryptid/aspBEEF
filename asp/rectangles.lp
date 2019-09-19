#const nrect = 1.
#const selectcount = 2.

rectangle(1..nrect).

valueid(I) :- value(I,_,_).

selectcount { selattr(A):attribute(A) } selectcount.

rectattr(R,A) :- rectangle(R), selattr(A).

attrval(A,V) :- value(_,A,V).

class(C) :- cluster(_,C).

1 { rectval(R,A,V0,V1) : attrval(A,V0), attrval(A,V1), V0 < V1} 1 :- rectattr(R,A).

rectsize(R, S) :- rectangle(R), S=#sum{ |V1-V0|,A : rectval(R,A,V0,V1), rectattr(R,A) }.

attrinlier(R,I,A) :- value(I,A,V), rectval(R,A,V0,V1), V >= V0, V <= V1.
attroutlier(R,I,A) :- value(I,A,V), rectval(R,A,V0,V1), V < V0.
attroutlier(R,I,A) :- value(I,A,V), rectval(R,A,V0,V1), V > V1.

rectoutlier(R, I) :- attroutlier(R,I,A).
rectinlier(R, I) :- attrinlier(R,I,A), not rectoutlier(R,I).

inlier(I) :- rectinlier(R, I).
outlier(I) :- valueid(I), not inlier(I).

rectinliercount(R,N) :- rectangle(R), N=#count{ I : rectinlier(R,I) }.
inliercount(I,N) :- value(I,A,V), N=#count{ R: rectinlier(R,I) }.
clustercount(R,CL,C) :- rectangle(R), class(CL), C=#count{ I : rectinlier(R,I), cluster(I,CL) }.

maxclustercount(R,M) :- rectangle(R), M=#max{ C : clustercount(R,CL,C) }.
dominantcluster(R, CL) :- clustercount(R, CL, M), maxclustercount(R, M).
impurity(R,N-M) :-  maxclustercount(R,M), rectinliercount(R,N).

overlapcount(C) :- C=#sum{ N,I : inliercount(I,N), N > 1 }.
outliercount(O) :- O=#count{ I : outlier(I) }.

:- rectangle(R), rectinliercount(R, 0).
:- class(CL), not dominantcluster(_, CL).


#minimize{ I: impurity(R,I) }.
%#minimize{ S,R: rectsize(R,S) }.
#minimize{ OU: outliercount(OU)  }.
#minimize{ OC: overlapcount(OC) }.


#show selattr/1.
#show rectattr/2.
#show rectval/4.
#show overlapcount/1.
#show outliercount/1.
#show impurity/2.
#show rectsize/2.


