%------------------------------------------------------------------------------
% File     : EXT027+1.p : extra test (transitivity/fresh_constant)
%------------------------------------------------------------------------------
fof(a1, axiom, a = b).
fof(a2, axiom, b = c).
fof(a3, axiom, d = e).
fof(c, conjecture, c = d).

