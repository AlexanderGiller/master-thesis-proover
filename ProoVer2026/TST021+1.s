%------------------------------------------------------------------------------
% File     : TST021+1.s : ProoVer 2026
% Proof    : Problems/TST021+1.p
% Test     : nc01_status_not_cth - negated_conjecture mit Status thm
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) => q(X)), file('Problems/TST021+1.p', a1)).

fof(a2, axiom, p(a), file('Problems/TST021+1.p', a2)).

fof(c1, conjecture, q(a), file('Problems/TST021+1.p', c1)).

fof(nc1, negated_conjecture, ~q(a), inference(negated_conjecture, [status(thm)], [c1])).

fof(f1, plain, q(a), inference(modus_ponens, [status(thm)], [a1, a2])).

fof(f2, plain, $false, inference(consequence, [status(thm)], [f1, nc1])).

% SZS output end Proof