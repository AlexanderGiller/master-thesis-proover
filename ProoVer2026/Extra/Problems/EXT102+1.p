%------------------------------------------------------------------------------
% File     : EXT102+1.p : extra test (modus_ponens/inconsistent_instance)
%------------------------------------------------------------------------------
fof(a1, axiom, ![X]: (p(X) => q(X,X))).
fof(a2, axiom, p(a)).
fof(c, conjecture, q(a,b)).

