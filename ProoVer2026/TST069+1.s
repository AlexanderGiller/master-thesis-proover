%------------------------------------------------------------------------------
% File     : TST069+1.s : ProoVer 2026
% Proof    : Problems/TST069+1.p
% Test     : cp01_conjecture_used_as_premise_for_false - $false direkt aus [c1, nc1]: Konjunktur als Praemisse (zirkulaer, ATP-seitig gueltig)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) => q(X)), file('Problems/TST069+1.p', a1)).

fof(a2, axiom, p(a), file('Problems/TST069+1.p', a2)).

fof(c1, conjecture, q(a), file('Problems/TST069+1.p', c1)).

fof(nc1, negated_conjecture, ~q(a), inference(negated_conjecture, [status(cth)], [c1])).

fof(f2, plain, $false, inference(consequence, [status(thm)], [c1, nc1])).

% SZS output end Proof