%------------------------------------------------------------------------------
% File     : TST010+1.p : ProoVer 2026
% Source   : ProoVer 2026
% Status   : Unknown
%------------------------------------------------------------------------------
% SZS output start ListOfFormulae
fof(a1, axiom, ?[X]: p(X)).

fof(a2, axiom, ?[Y]: q(Y)).

fof(a3, axiom, ![X]: (p(X) => ![Y]: (q(Y) => r(X,Y)))).

fof(c1, conjecture, ?[X]: ?[Y]: r(X,Y)).
% SZS output end ListOfFormulae
