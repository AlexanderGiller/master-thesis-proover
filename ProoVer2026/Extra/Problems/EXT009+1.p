%------------------------------------------------------------------------------
% File     : EXT009+1.p : extra test (resolution/swapped_literal_order)
%------------------------------------------------------------------------------
fof(a1, axiom, p(a) | q(a)).
fof(a2, axiom, ~p(a) | r(a)).
fof(c, conjecture, r(a) | q(a)).

