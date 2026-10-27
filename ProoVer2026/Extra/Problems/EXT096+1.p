%------------------------------------------------------------------------------
% File     : EXT096+1.p : extra test (paramodulation/reverse_orientation)
%------------------------------------------------------------------------------
fof(a1, axiom, p(g(a))).
fof(a2, axiom, ![X]: f(X) = g(X)).
fof(c, conjecture, p(f(a))).

