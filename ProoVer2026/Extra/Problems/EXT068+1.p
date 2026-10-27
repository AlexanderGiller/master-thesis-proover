%------------------------------------------------------------------------------
% File     : EXT068+1.p : extra test (conjunction/unsupported_operand)
%------------------------------------------------------------------------------
fof(a1, axiom, p(a)).
fof(a2, axiom, q(a)).
fof(c, conjecture, p(a) & r(a)).

