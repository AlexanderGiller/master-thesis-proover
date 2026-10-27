%------------------------------------------------------------------------------
% File     : EXT030+1.p : extra test (transitivity/status_cth)
%------------------------------------------------------------------------------
fof(a1, axiom, a = b).
fof(a2, axiom, b = c).
fof(a3, axiom, d = e).
fof(c, conjecture, a = c).

