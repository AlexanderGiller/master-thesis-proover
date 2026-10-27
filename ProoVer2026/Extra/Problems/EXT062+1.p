%------------------------------------------------------------------------------
% File     : EXT062+1.p : extra test (modus_ponens/affirming_consequent)
%------------------------------------------------------------------------------
fof(a1, axiom, p(a) => q(a)).
fof(a2, axiom, p(a)).
fof(a3, axiom, q(a)).
fof(c, conjecture, p(a)).

