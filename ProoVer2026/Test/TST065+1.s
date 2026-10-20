%------------------------------------------------------------------------------
% File     : TST065+1.s : ProoVer 2026
% Proof    : Problems/TST065+1.p
% Test     : nc08_no_negated_conjecture - Kein negated_conjecture-Schritt; $false wird aus q(a) 'abgeleitet'
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) => q(X)), file('Problems/TST065+1.p', a1)).

fof(a2, axiom, p(a), file('Problems/TST065+1.p', a2)).

fof(c1, conjecture, q(a), file('Problems/TST065+1.p', c1)).

fof(f1, plain, q(a), inference(modus_ponens, [status(thm)], [a1, a2])).

fof(f2, plain, $false, inference(consequence, [status(thm)], [f1])).

% SZS output end Proof