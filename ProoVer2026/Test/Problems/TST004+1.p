%------------------------------------------------------------------------------
% File     : TST004+1.p : ProoVer 2026
% Source   : ProoVer 2026
% Status   : Unknown
%------------------------------------------------------------------------------
% SZS output start ListOfFormulae
fof(a1, axiom, ![X]: ![Z]: ?[Y]: r(X,Z,Y)).

fof(a2, axiom, ![X]: ![Z]: ![Y]: (r(X,Z,Y) => s(X))).

fof(c1, conjecture, ![X]: s(X)).
% SZS output end ListOfFormulae
