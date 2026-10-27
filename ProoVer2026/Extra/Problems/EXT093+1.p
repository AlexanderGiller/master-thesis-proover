%------------------------------------------------------------------------------
% File     : EXT093+1.p : extra test (resolution/variables_standardised_apart)
%------------------------------------------------------------------------------
fof(a1, axiom, ![X]: (p(X, c) | q(X))).
fof(a2, axiom, ![X]: (~p(a, X) | r(X))).
fof(c, conjecture, q(a) | r(c)).

