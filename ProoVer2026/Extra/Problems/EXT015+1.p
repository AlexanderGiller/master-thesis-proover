%------------------------------------------------------------------------------
% File     : EXT015+1.p : extra test (paramodulation/same_parent_twice)
%------------------------------------------------------------------------------
fof(a1, axiom, p(f(a))).
fof(a2, axiom, ![X]: f(X) = g(X)).
fof(a3, axiom, ![X]: f(X) = h(X)).
fof(c, conjecture, p(g(a))).

