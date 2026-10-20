%------------------------------------------------------------------------------
% File     : TST052+1.s : ProoVer 2026
% Proof    : Problems/TST052+1.p
% Test     : c13_empty_premises_tautology - Schritt mit leerer Praemissenliste und Tautologie (zusaetzlicher Schritt)
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) => q(X)), file('Problems/TST052+1.p', a1)).

fof(a2, axiom, p(a), file('Problems/TST052+1.p', a2)).

fof(c1, conjecture, q(a), file('Problems/TST052+1.p', c1)).

fof(nc1, negated_conjecture, ~q(a), inference(negated_conjecture, [status(cth)], [c1])).

fof(f1, plain, q(a), inference(modus_ponens, [status(thm)], [a1, a2])).

fof(f2, plain, $false, inference(consequence, [status(thm)], [f1, nc1])).

fof(t1, plain, (p(a) | ~p(a)), inference(tautology, [status(thm)], [])).

% SZS output end Proof