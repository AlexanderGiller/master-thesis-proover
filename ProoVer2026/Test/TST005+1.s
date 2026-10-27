%------------------------------------------------------------------------------
% File     : TST005+1.s : ProoVer 2026
% Proof    : Problems/TST005+1.p
% Test     : c05_two_independent_skolem_symbols - Zwei Skolemisierungen mit verschiedenen neuen Symbolen
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ?[X]: p(X), file('Problems/TST005+1.p', a1)).

fof(a2, axiom, ?[Y]: q(Y), file('Problems/TST005+1.p', a2)).

fof(a3, axiom, ![X]: (p(X) => ![Y]: (q(Y) => r(X,Y))), file('Problems/TST005+1.p', a3)).

fof(c1, conjecture, ?[X]: ?[Y]: r(X,Y), file('Problems/TST005+1.p', c1)).

fof(nc1, negated_conjecture, ~?[X]: ?[Y]: r(X,Y), inference(negated_conjecture, [status(cth)], [c1])).

fof(s1, plain, p(sK0), inference(skolemize, [status(esa), new_symbols(skolem, [sK0]), skolemize(X, sK0)], [a1])).

fof(s2, plain, q(sK1), inference(skolemize, [status(esa), new_symbols(skolem, [sK1]), skolemize(Y, sK1)], [a2])).

fof(f1, plain, ![Y]: (q(Y) => r(sK0,Y)), inference(modus_ponens, [status(thm)], [a3, s1])).

fof(f2, plain, r(sK0,sK1), inference(modus_ponens, [status(thm)], [f1, s2])).

fof(f3, plain, ~r(sK0,sK1), inference(instantiate, [status(thm)], [nc1])).

fof(f4, plain, $false, inference(consequence, [status(thm)], [f2, f3])).

% SZS output end Proof