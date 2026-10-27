%------------------------------------------------------------------------------
% File     : EXT073+1.p : extra test (split_conjunct/parent_is_disjunction)
%------------------------------------------------------------------------------
fof(a1, axiom, p(a) & q(a)).
fof(a2, axiom, p(a) | q(a)).
fof(c, conjecture, q(a)).

