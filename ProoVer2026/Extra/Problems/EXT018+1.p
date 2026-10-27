%------------------------------------------------------------------------------
% File     : EXT018+1.p : extra test (paramodulation/under_quantifier_wrong)
%------------------------------------------------------------------------------
fof(a1, axiom, ![Y]: p(f(Y))).
fof(a2, axiom, ![X]: f(X) = c).
fof(c, conjecture, ![Y]: p(f(c))).

