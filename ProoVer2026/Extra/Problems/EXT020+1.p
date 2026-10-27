%------------------------------------------------------------------------------
% File     : EXT020+1.p : extra test (paramodulation/one_occurrence_wrong)
%------------------------------------------------------------------------------
fof(a1, axiom, p(f(a), f(a))).
fof(a2, axiom, ![X]: f(X) = g(X)).
fof(c, conjecture, p(g(a), g(b))).

