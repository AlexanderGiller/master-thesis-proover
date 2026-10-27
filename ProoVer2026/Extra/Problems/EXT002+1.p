%------------------------------------------------------------------------------
% File     : EXT002+1.p : extra test (resolution/wrong_conclusion_and)
%------------------------------------------------------------------------------
fof(a1, axiom, ![X]: (p(X) | q(X))).
fof(a2, axiom, ![X]: (~p(X) | r(X))).
fof(a3, axiom, ![X]: (u(X) | r(X))).
fof(c, conjecture, ![X]: (q(X) & r(X))).

