%------------------------------------------------------------------------------
% File     : TST055+1.p : ProoVer 2026
% Source   : ProoVer 2026
% Status   : Unknown
%------------------------------------------------------------------------------
% SZS output start ListOfFormulae
fof(a1, axiom, ![X]: ?[Y]: ![Z]: ?[W]: r(X,Y,Z,W)).

fof(a2, axiom, ![X]: ![Y]: ![Z]: ![W]: (r(X,Y,Z,W) => s(X))).

fof(c1, conjecture, ![X]: s(X)).
% SZS output end ListOfFormulae
