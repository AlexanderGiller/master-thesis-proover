%------------------------------------------------------------------------------
% File     : TST001+1.s : ProoVer 2026
% Proof    : Problems/TST001+1.p
% Test     : c01_basic_modus_ponens - Einfacher korrekter Beweis ohne Skolemisierung
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) => q(X)), file('Problems/TST001+1.p', a1)).

fof(a2, axiom, p(a), file('Problems/TST001+1.p', a2)).

fof(c1, conjecture, q(a), file('Problems/TST001+1.p', c1)).

fof(nc1, negated_conjecture, ~q(a), inference(negated_conjecture, [status(cth)], [c1])).

fof(f1, plain, q(a), inference(modus_ponens, [status(thm)], [a1, a2])).

fof(f2, plain, $false, inference(consequence, [status(thm)], [f1, nc1])).

% SZS output end Proof