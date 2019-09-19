#const nrect = 1.
#const selectcount = 2.

rectangle(1..nrect).

valueid(I) :- value(I,_,_).

selectcount { selattr(A):attribute(A) } selectcount.

rectattr(R,A) :- rectangle(R), selattr(A).

attrval(A,V) :- value(_,A,V).

1 { rectval(R,A,V0,V1) : attrval(A,V0), attrval(A,V1), V0 < V1} 1 :- rectattr(R,A).

attrinlier(R,I,A) :- value(I,A,V), rectval(R,A,V0,V1), V >= V0, V <= V1.
attroutlier(R,I,A) :- value(I,A,V), rectval(R,A,V0,V1), V < V0.
attroutlier(R,I,A) :- value(I,A,V), rectval(R,A,V0,V1), V > V1.

rectoutlier(R, I) :- attroutlier(R,I,A).
rectinlier(R, I) :- attrinlier(R,I,A), not rectoutlier(R,I).

inlier(I) :- rectinlier(R, I).
outlier(I) :- valueid(I), not inlier(I).

rectinliercount(R,N) :- rectangle(R), N=#count{ I : rectinlier(R,I) }.
inliercount(I,N) :- value(I,A,V), N=#count{ R: rectinlier(R,I) }.

overlapfeat(R1, R2, A) :- rectangle(R1), rectangle(R2), R1 != R2,
            rectval(R1, A, V10, V11), rectval(R2, A, V20, V21), 
            V20 < V11, V21 > V11.
overlapfeat(R1, R2, A) :- rectangle(R1), rectangle(R2), R1 != R2,
            rectval(R1, A, V10, V11), rectval(R2, A, V20, V21), 
            V20 >= V10, V21 <= V11.

overlapfeat(R2, R1, A) :- overlapfeat(R1, R2, A).

%% Doesn't work with rectattr/selattr, maybe some loop in grounding?
%% Attribute(A) is not working because attribute includes clustering attribute and 
%% all of the other not-selected attributes.
parallel(R1, R2) :- attribute(A), not overlapfeat(R1, R2, A), not overlapfeat(R2,R1,A),
                    rectangle(R1), rectangle(R2), R1 != R2.
ov(R1, R2) :- overlapfeat(R1, R2, A), not parallel(R1, R2).
contains(R1, R2) :- ov(R1,R2), ov(R2, R1), R1 < R2.
overlaps(R1, R2) :- ov(R1, R2), not contains(R1, R2).

overlaplenght(R1,R2,A,L) :- overlaps(R1, R2), overlapfeat(R1, R2, A),
                        rectval(R1, A, V10, V11), rectval(R2, A, V20, V21), 
                        L=|V11-V20|.
overlapsum(R1,R2,S) :- overlaps(R1,R2), S=#sum{ L,A: overlaplenght(R1,R2,A,L) }.
overlaptotal(O) :- O=#sum{ S,R1,R2: overlapsum(R1,R2,S) }.

overlapcount(C) :- C=#sum{ N,I : inliercount(I,N), N > 1 }.
outliercount(O) :- O=#count{ I : outlier(I) }.

:- rectangle(R), rectinliercount(R, 0).

#minimize{ OU: outliercount(OU) }.
#minimize{ OC: overlapcount(OC) }.
#minimize{ OV: overlaptotal(OV) }.

#show rectattr/2.
#show rectval/4.
#show overlapcount/1.
#show overlapfeat/3.
#show parallel/2.
#show overlaps/2.
#show overlaptotal/1.
#show outliercount/1.
#show selattr/1.

