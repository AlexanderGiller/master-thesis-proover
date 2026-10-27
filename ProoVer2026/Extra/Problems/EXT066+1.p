%------------------------------------------------------------------------------
% File     : EXT066+1.p : extra test (modus_ponens/universal_wrong_instance)
%------------------------------------------------------------------------------
fof(a1, axiom, ![X]: (p(X) => q(X))).
fof(a2, axiom, p(a)).
fof(c, conjecture, q(b)).

