%------------------------------------------------------------------------------
% File     : EXT098+1.p : extra test (paramodulation/target_needs_instantiation)
%------------------------------------------------------------------------------
fof(a1, axiom, ![X]: p(f(X))).
fof(a2, axiom, f(a) = c).
fof(c, conjecture, p(c)).

