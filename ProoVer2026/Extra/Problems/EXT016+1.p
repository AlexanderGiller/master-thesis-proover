%------------------------------------------------------------------------------
% File     : EXT016+1.p : extra test (paramodulation/status_cth)
%------------------------------------------------------------------------------
fof(a1, axiom, p(f(a))).
fof(a2, axiom, ![X]: f(X) = g(X)).
fof(a3, axiom, ![X]: f(X) = h(X)).
fof(c, conjecture, p(g(a))).

