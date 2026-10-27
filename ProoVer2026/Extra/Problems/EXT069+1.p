%------------------------------------------------------------------------------
% File     : EXT069+1.p : extra test (conjunction/single_parent_repeated)
%------------------------------------------------------------------------------
fof(a1, axiom, p(a)).
fof(a2, axiom, q(a)).
fof(c, conjecture, p(a) & q(a)).

