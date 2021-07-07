asprin version 3.1.0
Reading from asp/rectangles_asprin.lp
#program base.
_end.

_end.

_end.

_end.

_end.


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


_end.

_end.

_end.

_end.


_end.


#show minrectval/4.
#show rectinliercount/2.
#show rectcluster/2.
#show outliercount/1.
#show overlapcount/1.
#show impurecount/1.
#show selattr/1.
_end.
% MIT License
% 
% Copyright (c) 2018 Javier Romero
% 
% Permission is hereby granted, free of charge, to any person obtaining a copy
% of this software and associated documentation files (the "Software"), to deal
% in the Software without restriction, including without limitation the rights
% to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
% copies of the Software, and to permit persons to whom the Software is
% furnished to do so, subject to the following conditions:
% 
% The above copyright notice and this permission notice shall be included in all
% copies or substantial portions of the Software.
% 
% THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
% IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
% FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
% AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
% LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
% OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
% SOFTWARE.
% -*- coding: utf-8 -*-

_end.
#program generate.

#program specification.
_preference(overlap,less(cardinality)).
_preference(overlap,(1,1,(R1,I,R2)),1,for(atom(overlappoint(I,R1,R2))),()) :- rectangle(R1), rectangle(R2), pointid(I).
_holds(atom(overlappoint(I,R1,R2)),0) :- overlappoint(I,R1,R2), rectangle(R1), rectangle(R2), pointid(I).

_preference(impurity,less(cardinality)).
_preference(impurity,(2,1,(I)),1,for(atom(impurepoint(I))),()) :- pointid(I).
_holds(atom(impurepoint(I)),0) :- impurepoint(I), pointid(I).

_preference(outlier,less(cardinality)).
_preference(outlier,(3,1,(I)),1,for(atom(outlier(I))),()) :- pointid(I).
_holds(atom(outlier(I)),0) :- outlier(I), pointid(I).

_preference(all,lexico).
_preference(all,(4,1,()),1,name(overlap),(overlapprio)).
_preference(all,(4,2,()),1,name(impurity),(impurityprio)).
_preference(all,(4,3,()),1,name(outlier),(outlierprio)).

_optimize(all).



_true.


_pref_dom(X) :- _preference(X,_).


#program preference(_m1,_m2).
_unsat(_m(_m1),_m(_m2)) :- not __better(P); _optimize(P); _volatile(_m(_m1),_m(_m2)).
#program preference_base.
__required(P,better) :- _optimize(P).
#defined _optimize/1.
#defined __better/1.
#defined __required/2.
#defined __error/1.
#defined __error_type/2.
__error(("preference:",P,": error: preference specification error, type '",T,"' does not allow formulas.")) :- _preference(P,T); __error_type(T,no_formulas); _preference(P,_,_,for(X),_).
__error(("preference:",P,": error: preference specification error, type '",T,"' requires weight tuples.")) :- _preference(P,T); __error_type(T,yes_weights); _preference(P,_,_,_,W); W=().
__error(("preference:",P,": error: preference specification error, type '",T,"' does not allow weights.")) :- _preference(P,T); __error_type(T,no_weights); _preference(P,_,_,_,W); W!=().
__error(("preference:",P,": error: preference specification error, type '",T,"' does not allow using '>>'.")) :- _preference(P,T); __error_type(T,no_ordering); _preference(P,_,R,_,_); R>1.
__error(("preference:",P,": error: preference specification error, type '",T,"' requires at least ",(N-1),"'>>'s.")) :- _preference(P,T); __error_type(T,ordering_min_length(N)); N>1; not _preference(P,_,N,_,_).
__error(("preference:",P,": error: preference specification error, type '",T,"' allows at most ",(N-1),"'>>'s.")) :- _preference(P,T); __error_type(T,ordering_max_length(N)); _preference(P,_,R,_,_); R>N.
__error(("preference:",P,": error: preference specification error, type '",T,"' does not allow sets.")) :- _preference(P,T); __error_type(T,no_sets); _preference(P,E,S,X,_); _preference(P,E,S,Y,_); X>Y.
__error(("preference:",P,": error: preference specification error, type '",T,"' does not allow sets at position",S,".")) :- _preference(P,T); __error_type(T,no_sets(S)); _preference(P,E,S,X,_); _preference(P,E,S,Y,_); X>Y.
__error(("preference:",P,": error: preference specification error, type '",T,"' does not allow naming atoms.")) :- _preference(P,T); __error_type(T,no_naming); _preference(P,_,_,name(X),_).
__error(("preference:",P,": error: preference specification error, type '",T,"' does not allow more than one preference element.")) :- _preference(P,T); __error_type(T,single); 2 <= { _preference(P,_,_,_,_) :  }.
__error(("preference:",P,": error: preference specification error, type '",T,"' does not allow using '||'.")) :- _preference(P,T); __error_type(T,no_condition); _preference(P,_,0,_,_).
__error(("preference:",P,": error: preference specification error, type '",T,"' requires a weight tuple of at least ",N," elements.")) :- _preference(P,T); __error_type(T,(min_weight_length,N)); _preference(P,_,_,_,W); @length(W)<N.
__error(("preference:",P,": error: preference specification error, type '",T,"' requires a weight tuple of at most ",N," elements.")) :- _preference(P,T); __error_type(T,(max_weight_length,N)); _preference(P,_,_,_,W); @length(W)>N.
__error(("preference:",P,": error: preference specification error, type '",T,"' requires different weights for every named preference statement")) :- _preference(P,T); __error_type(T,naming_unique_weights); _preference(P,_,_,name(P1),W); _preference(P,_,_,name(P2),W); P1!=P2.
#program weak.
:~ ___wc(P,W,L,T,X); _optimize(P); _holds(X,0). [W@L,T]
#defined ___wc/5.
___bit(P,G,B) :- ___as_minmax(P); ___elem(P,G,_,_,_); S = #sum { W,T : ___elem(P,G,W,T,X), W>0; -W,T : ___elem(P,G,W,T,X), W<0 }; B=(0..(@log2up((S+1))-1)).
{ ___true(bit(P,G,B)) :  } :- ___as_minmax(P); ___bit(P,G,B).
#false :- ___as_minmax(P); ___elem(P,G,_,_,_); 0 != #sum { -@exp2(B) : ___true(bit(P,G,B)); W,T : ___elem(P,G,W,T,X), W>0, _holds(X,0); -W,T : ___elem(P,G,W,T,X), W<0, not _holds(X,0) }.
_holds(bit(P,B),0) :- ___as_minmax(P); ___true(bit(P,G,B)); not ___not_max(P,G,B).
___not_max(P,G,(B-1)) :- ___as_minmax(P); not ___true(bit(P,G,B)); _holds(bit(P,B),0); B>0; ___elem(P,G,_,_,_).
___not_max(P,G,(B-1)) :- ___as_minmax(P); ___not_max(P,G,B); B>0.
___wc(P,1,(B+1),0,bit(P,B)) :- ___as_minmax(P); ___bit(P,_,B).
___levels(P,L) :- ___as_minmax(P); L = #sum { 1,B : ___bit(P,_,B) }.
#defined ___as_minmax/1.
#defined ___elem/5.
#defined ___bit/3.
___wc(P,W,(L+S),T,X) :- ___as_lexico(P); ___level(P,P1,L1); ___wc(P1,W,L,T,X); S = #sum { LS2,P2,L2 : ___level(P,P2,L2), L2<L1, ___levels(P2,LS2) }.
___max_level(P,MAX) :- ___as_lexico(P); MAX = #max { L : ___level(P,_,L) }.
___sum_levels(P,(MIN-1),0) :- ___as_lexico(P); MIN = #min { L : ___level(P,_,L) }.
___sum_levels(P,(L+1),S) :- ___as_lexico(P); ___sum_levels(P,L,S); ___max_level(P,MAX); L<MAX.
___sum_levels(P,(L+1),(SS+S)) :- ___as_lexico(P); ___sum_levels(P,L,S); ___level(P,P1,(L+1)); ___levels(P1,SS).
___levels(P,S) :- ___as_lexico(P); ___max_level(P,MAX); S = #max { SS : ___sum_levels(P,MAX,SS); 0 :  }.
#defined ___as_lexico/1.
#defined ___level/3.
