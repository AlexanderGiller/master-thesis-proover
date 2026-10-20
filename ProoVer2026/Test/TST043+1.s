%------------------------------------------------------------------------------
% File     : TST043+1.s : ProoVer 2026
% Proof    : Problems/TST043+1.p
% Test     : st08_monolithic_step - Ein Schritt $false aus Axiomen+nc (faktisch Re-Check der ganzen Konjunktur; Granularitaet)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) => q(X)), file('Problems/TST043+1.p', a1)).

fof(a2, axiom, p(a), file('Problems/TST043+1.p', a2)).

fof(c1, conjecture, q(a), file('Problems/TST043+1.p', c1)).

fof(nc1, negated_conjecture, ~q(a), inference(negated_conjecture, [status(cth)], [c1])).

fof(f1, plain, $false, inference(consequence, [status(thm)], [a1, a2, nc1])).

% SZS output end Proof