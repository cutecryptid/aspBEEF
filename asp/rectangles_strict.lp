#const nrect = 1.
#const selectcount = 2.

rectangle(1..nrect).

selectcount { selattr(A):attribute(A) } selectcount.

rectattr(R,A) :- rectangle(R), selattr(A).

1 { rectval(R,A,V0,V1) : value(_,A,V0), value(_,A,V1), V0 < V1} 1 :- rectangle(R), selattr(A).

attrinlier(R,I,A) :- value(I,A,V), rectval(R,A,V0,V1), V >= V0, V <= V1.
partialinlier(R,I,SA,OA) :- attrinlier(R,I,SA), selattr(SA), selattr(OA), SA != OA, value(I,OA,V), 
                                not attrinlier(R,I,OA).

outlier(I) :- partialinlier(R,I,SA,OA).
outlier(I) :- value(I,A,V), not attrinlier(_,I,_).

inlier(I) :- attrinlier(R,I,A), not outlier(I).

attroverlaps(R1,R2,A,O) :- rectval(R1,A,V10, V11), rectval(R2,A,V20,V21), R1 < R2,
                        V20 >= V10, V20 <= V11, O = |V11-V20|.

partialoverlaps(R1,R2,SA,OA) :- attroverlaps(R1,R2,SA,O), selattr(SA), selattr(OA), SA < OA, 
                                    not attroverlaps(R1,R2,OA,O).

overlaps(R1,R2) :- attroverlaps(R1,R2,_,_), not partialoverlaps(R1,R2,_,_).
overlapamount(R1,R2,N) :- overlaps(R1, R2), N = #sum{ O,A : attroverlaps(R1, R2, A, O) }.

:- outlier(I).

#show rectval/4.
#show overlaps/2.
#show overlapamount/3.