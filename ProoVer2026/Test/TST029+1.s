%------------------------------------------------------------------------------
% File     : TST029+1.s : ProoVer 2026
% Proof    : Problems/TST029+1.p
% Test     : ax02_nonexistent_name - file-Direktive verweist auf nicht existierendes Axiom a9
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) => q(X)), file('Problems/TST029+1.p', a1)).

fof(a2, axiom, p(a), file('Problems/TST029+1.p', a9)).

fof(c1, conjecture, q(a), file('Problems/TST029+1.p', c1)).

fof(nc1, negated_conjecture, ~q(a), inference(negated_conjecture, [status(cth)], [c1])).

fof(f1, plain, q(a), inference(modus_ponens, [status(thm)], [a1, a2])).

fof(f2, plain, $false, inference(consequence, [status(thm)], [f1, nc1])).

% SZS output end Proof