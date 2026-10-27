%------------------------------------------------------------------------------
% File     : TST068+1.s : ProoVer 2026
% Proof    : Problems/TST068+1.p
% Test     : nc11_two_negated_conjectures - Edge: zwei (korrekte) negated_conjecture-Schritte fuer dieselbe Konjunktur
% Expected : EDGE
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) => q(X)), file('Problems/TST068+1.p', a1)).

fof(a2, axiom, p(a), file('Problems/TST068+1.p', a2)).

fof(c1, conjecture, q(a), file('Problems/TST068+1.p', c1)).

fof(nc1, negated_conjecture, ~q(a), inference(negated_conjecture, [status(cth)], [c1])).

fof(f1, plain, q(a), inference(modus_ponens, [status(thm)], [a1, a2])).

fof(f2, plain, $false, inference(consequence, [status(thm)], [f1, nc1])).

fof(nc2, negated_conjecture, ~q(a), inference(negated_conjecture, [status(cth)], [c1])).

% SZS output end Proof