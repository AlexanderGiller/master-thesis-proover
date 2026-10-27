%------------------------------------------------------------------------------
% File     : EXT028+1.p : extra test (transitivity/no_common_term)
%------------------------------------------------------------------------------
fof(a1, axiom, a = b).
fof(a2, axiom, b = c).
fof(a3, axiom, d = e).
fof(c, conjecture, a = e).

