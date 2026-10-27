%------------------------------------------------------------------------------
% File     : EXT019+1.p : extra test (paramodulation/one_occurrence)
%------------------------------------------------------------------------------
fof(a1, axiom, p(f(a), f(a))).
fof(a2, axiom, ![X]: f(X) = g(X)).
fof(c, conjecture, p(g(a), f(a))).

