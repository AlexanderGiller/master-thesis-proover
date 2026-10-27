%------------------------------------------------------------------------------
% File     : EXT012+1.p : extra test (paramodulation/wrong_symbol)
%------------------------------------------------------------------------------
fof(a1, axiom, p(f(a))).
fof(a2, axiom, ![X]: f(X) = g(X)).
fof(a3, axiom, ![X]: f(X) = h(X)).
fof(c, conjecture, p(h(a))).

