%------------------------------------------------------------------------------
% File     : TST058+1.p : ProoVer 2026
% Source   : ProoVer 2026
% Status   : Unknown
%------------------------------------------------------------------------------
% SZS output start ListOfFormulae
fof(a1, axiom, ?[X]: p(X)).

fof(a2, axiom, ![X]: (p(X) => q(X))).

fof(a3, axiom, ~q(a)).

fof(c1, conjecture, ?[X]: q(X)).
% SZS output end ListOfFormulae
