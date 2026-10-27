%------------------------------------------------------------------------------
% File     : TST017+1.s : ProoVer 2026
% Proof    : Problems/TST017+1.p
% Test     : sk10_wrong_polarity - ~?[X]:q(X) wird wie ein positives Existenz-Axiom skolemisiert (~q(sK1)) - unsound
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ?[X]: p(X), file('Problems/TST017+1.p', a1)).

fof(a2, axiom, ![X]: (p(X) => q(X)), file('Problems/TST017+1.p', a2)).

fof(c1, conjecture, ?[X]: q(X), file('Problems/TST017+1.p', c1)).

fof(nc1, negated_conjecture, ~?[X]: q(X), inference(negated_conjecture, [status(cth)], [c1])).

fof(s1, plain, p(sK0), inference(skolemize, [status(esa), new_symbols(skolem, [sK0]), skolemize(X, sK0)], [a1])).

fof(f1, plain, q(sK0), inference(modus_ponens, [status(thm)], [a2, s1])).

fof(f2, plain, ~q(sK0), inference(instantiate, [status(thm)], [nc1])).

fof(f3, plain, $false, inference(consequence, [status(thm)], [f1, f2])).

fof(s2, plain, ~q(sK1), inference(skolemize, [status(esa), new_symbols(skolem, [sK1]), skolemize(X, sK1)], [nc1])).

% SZS output end Proof