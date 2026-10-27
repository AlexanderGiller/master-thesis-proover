%------------------------------------------------------------------------------
% File     : TST049+1.s : ProoVer 2026
% Proof    : Problems/TST049+1.p
% Test     : c10_nested_existentials_outer_first - ?[X]?[Y]: aeusserer zuerst, zwei Skolem-Konstanten in zwei Schritten
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ?[X]: ?[Y]: r(X,Y), file('Problems/TST049+1.p', a1)).

fof(a2, axiom, ![X]: ![Y]: (r(X,Y) => s), file('Problems/TST049+1.p', a2)).

fof(c1, conjecture, s, file('Problems/TST049+1.p', c1)).

fof(nc1, negated_conjecture, ~s, inference(negated_conjecture, [status(cth)], [c1])).

fof(s1, plain, ?[Y]: r(sK0,Y), inference(skolemize, [status(esa), new_symbols(skolem, [sK0]), skolemize(X, sK0)], [a1])).

fof(s2, plain, r(sK0,sK1), inference(skolemize, [status(esa), new_symbols(skolem, [sK1]), skolemize(Y, sK1)], [s1])).

fof(f1, plain, (r(sK0,sK1) => s), inference(instantiate, [status(thm)], [a2])).

fof(f2, plain, s, inference(modus_ponens, [status(thm)], [f1, s2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [nc1, f2])).

% SZS output end Proof