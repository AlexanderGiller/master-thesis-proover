%------------------------------------------------------------------------------
% File     : TST012+1.s : ProoVer 2026
% Proof    : Problems/TST012+1.p
% Test     : sk05_vacuous_universal_omitted - Edge (laut Regel 'exakt'): sK0(X) statt sK0(X,Z); Z ist im Scope, kommt aber nicht vor
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: ![Z]: ?[Y]: r(X,Z,Y), file('Problems/TST012+1.p', a1)).

fof(a2, axiom, ![X]: ![Z]: ![Y]: (r(X,Z,Y) => s(X)), file('Problems/TST012+1.p', a2)).

fof(c1, conjecture, ![X]: s(X), file('Problems/TST012+1.p', c1)).

fof(nc1, negated_conjecture, ~![X]: s(X), inference(negated_conjecture, [status(cth)], [c1])).

fof(s1, plain, ![X]: ![Z]: r(X,Z,sK0(X)), inference(skolemize, [status(esa), new_symbols(skolem, [sK0]), skolemize(Y, sK0(X))], [a1])).

fof(s2, plain, ~s(sK1), inference(skolemize, [status(esa), new_symbols(skolem, [sK1]), skolemize(X, sK1)], [nc1])).

fof(f1, plain, r(sK1, sK1, sK0(sK1,sK1)), inference(instantiate, [status(thm)], [s1])).

fof(f2, plain, s(sK1), inference(modus_ponens, [status(thm)], [a2, f1])).

fof(f3, plain, $false, inference(consequence, [status(thm)], [f2, s2])).

% SZS output end Proof