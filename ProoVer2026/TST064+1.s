%------------------------------------------------------------------------------
% File     : TST064+1.s : ProoVer 2026
% Proof    : Problems/TST064+1.p
% Test     : sk25_existential_in_antecedent - ?[X] im Antezedens (negative Polaritaet): p(sK0) => q ist keine korrekte Skolemisierung (zusaetzlicher Schritt)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ((?[X]: p(X)) => q), file('Problems/TST064+1.p', a1)).

fof(a2, axiom, p(b), file('Problems/TST064+1.p', a2)).

fof(c1, conjecture, q, file('Problems/TST064+1.p', c1)).

fof(nc1, negated_conjecture, ~q, inference(negated_conjecture, [status(cth)], [c1])).

fof(f1, plain, q, inference(modus_ponens, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [nc1, f1])).

fof(s1, plain, (p(sK0) => q), inference(skolemize, [status(esa), new_symbols(skolem, [sK0]), skolemize(X, sK0)], [a1])).

% SZS output end Proof