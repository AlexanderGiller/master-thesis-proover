%------------------------------------------------------------------------------
% File     : TST061+1.s : ProoVer 2026
% Proof    : Problems/TST061+1.p
% Test     : sk22_skolemize_conjecture - Skolemisierung der KONJUNKTUR (statt der Negation) - beweist die Konjunktur zirkulaer
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ?[X]: p(X), file('Problems/TST061+1.p', a1)).

fof(a2, axiom, ![X]: (p(X) => q(X)), file('Problems/TST061+1.p', a2)).

fof(c1, conjecture, ?[X]: q(X), file('Problems/TST061+1.p', c1)).

fof(nc1, negated_conjecture, ~?[X]: q(X), inference(negated_conjecture, [status(cth)], [c1])).

fof(s2, plain, q(sK1), inference(skolemize, [status(esa), new_symbols(skolem, [sK1]), skolemize(X, sK1)], [c1])).

fof(f2, plain, ~q(sK1), inference(instantiate, [status(thm)], [nc1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [s2, f2])).

% SZS output end Proof