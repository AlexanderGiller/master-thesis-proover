%------------------------------------------------------------------------------
% File     : TST007+1.s : ProoVer 2026
% Proof    : Problems/TST007+1.p
% Test     : c07_unordered_steps - Schritte in beliebiger Reihenfolge (Vorwaertsreferenzen erlaubt)
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(f2, plain, $false, inference(consequence, [status(thm)], [f1, nc1])).

fof(f1, plain, q(a), inference(modus_ponens, [status(thm)], [a1, a2])).

fof(nc1, negated_conjecture, ~q(a), inference(negated_conjecture, [status(cth)], [c1])).

fof(c1, conjecture, q(a), file('Problems/TST007+1.p', c1)).

fof(a2, axiom, p(a), file('Problems/TST007+1.p', a2)).

fof(a1, axiom, ![X]: (p(X) => q(X)), file('Problems/TST007+1.p', a1)).

% SZS output end Proof