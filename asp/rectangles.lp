#const nrect = 1.
#const selectcount = 2.

rectangle(1..nrect).

valueid(I) :- value(I,_,_).

selectcount { selattr(A):attribute(A) } selectcount.

rectattr(R,A) :- rectangle(R), selattr(A).

attrval(A,V) :- value(_,A,V).

1 { rectval(R,A,V0,V1) : attrval(A,V0), attrval(A,V1), V0 <= V1} 1 :- rectattr(R,A).

attrinlier(R,I,A) :- value(I,A,V), rectval(R,A,V0,V1), V >= V0, V <= V1.
attroutlier(R,I,A) :- value(I,A,V), rectval(R,A,V0,V1), V < V0.
attroutlier(R,I,A) :- value(I,A,V), rectval(R,A,V0,V1), V > V1.

rectoutlier(R, I) :- attroutlier(R,I,A).
rectinlier(R, I) :- attrinlier(R,I,A), not rectoutlier(R,I).

inlier(I) :- rectinlier(R, I).
outlier(I) :- valueid(I), not inlier(I).

rectinliercount(R,N) :- rectangle(R), N=#count{ I : rectinlier(R,I) }.
inliercount(I,N) :- value(I,A,V), N=#count{ R: rectinlier(R,I) }.

overlapcount(C) :- C=#sum{ N,I : inliercount(I,N), N > 1 }.
outliercount(O) :- O=#count{ I : outlier(I) }.

%rectsize(R, S) :- rectangle(R), S=#sum{ |V0-V1|,A : rectval(R,A,V0,V1) }.

:- rectangle(R), rectinliercount(R, 0).

#minimize{ OU: outliercount(OU) }.
#minimize{ OV: overlapcount(OV) }.
%#minimize{ R,S: rectsize(R, S)}.

#show rectval/4.
#show overlapcount/1.
#show outliercount/1.
%#show rectsize/2.

