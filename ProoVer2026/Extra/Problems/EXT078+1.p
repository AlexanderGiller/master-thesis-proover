%------------------------------------------------------------------------------
% File     : EXT078+1.p : extra test (remove_double_negation/single_negation_parent)
%------------------------------------------------------------------------------
fof(a1, axiom, ~~p(a)).
fof(a2, axiom, ~p(a)).
fof(c, conjecture, p(a)).

