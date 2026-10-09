%------------------------------------------------------------------------------
% File     : TST015+1.s : ProoVer 2026
% Proof    : Problems/TST015+1.p
% Test     : sk08_wrong_resulting_formula - Ergebnisformel vertauscht Argumente: r(sK0(X),X)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: ?[Y]: r(X,Y), file('Problems/TST015+1.p', a1)).

fof(a2, axiom, ![X]: ![Y]: (r(X,Y) => s(X)), file('Problems/TST015+1.p', a2)).

fof(c1, conjecture, ![X]: s(X), file('Problems/TST015+1.p', c1)).

fof(nc1, negated_conjecture, ~![X]: s(X), inference(negated_conjecture, [status(cth)], [c1])).

fof(s1, plain, ![X]: r(sK0(X), X), inference(skolemize, [status(esa), new_symbols(skolem, [sK0]), skolemize(Y, sK0(X))], [a1])).

fof(s2, plain, ~s(sK1), inference(skolemize, [status(esa), new_symbols(skolem, [sK1]), skolemize(X, sK1)], [nc1])).

fof(f1, plain, r(sK1, sK0(sK1)), inference(instantiate, [status(thm)], [s1])).

fof(f2, plain, s(sK1), inference(modus_ponens, [status(thm)], [a2, f1])).

fof(f3, plain, $false, inference(consequence, [status(thm)], [f2, s2])).

% SZS output end Proof