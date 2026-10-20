%------------------------------------------------------------------------------
% File     : TST036+1.s : ProoVer 2026
% Proof    : Problems/TST036+1.p
% Test     : st01_no_false - Beweis endet nicht in $false
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) => q(X)), file('Problems/TST036+1.p', a1)).

fof(a2, axiom, p(a), file('Problems/TST036+1.p', a2)).

fof(c1, conjecture, q(a), file('Problems/TST036+1.p', c1)).

fof(nc1, negated_conjecture, ~q(a), inference(negated_conjecture, [status(cth)], [c1])).

fof(f1, plain, q(a), inference(modus_ponens, [status(thm)], [a1, a2])).

% SZS output end Proof