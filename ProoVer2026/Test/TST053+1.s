%------------------------------------------------------------------------------
% File     : TST053+1.s : ProoVer 2026
% Proof    : Problems/TST053+1.p
% Test     : sk14_missing_scope_var_Z - sK1(X) statt sK1(X,Z): Z ist fuer W im Scope
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: ?[Y]: ![Z]: ?[W]: r(X,Y,Z,W), file('Problems/TST053+1.p', a1)).

fof(a2, axiom, ![X]: ![Y]: ![Z]: ![W]: (r(X,Y,Z,W) => s(X)), file('Problems/TST053+1.p', a2)).

fof(c1, conjecture, ![X]: s(X), file('Problems/TST053+1.p', c1)).

fof(nc1, negated_conjecture, ~![X]: s(X), inference(negated_conjecture, [status(cth)], [c1])).

fof(s1, plain, ![X]: ![Z]: ?[W]: r(X,sK0(X),Z,W), inference(skolemize, [status(esa), new_symbols(skolem, [sK0]), skolemize(Y, sK0(X))], [a1])).

fof(s2, plain, ![X]: ![Z]: r(X,sK0(X),Z,sK1(X)), inference(skolemize, [status(esa), new_symbols(skolem, [sK1]), skolemize(W, sK1(X))], [s1])).

fof(s3, plain, ~s(sK2), inference(skolemize, [status(esa), new_symbols(skolem, [sK2]), skolemize(X, sK2)], [nc1])).

fof(f1, plain, r(sK2,sK0(sK2),sK2,sK1(sK2)), inference(instantiate, [status(thm)], [s2])).

fof(f2, plain, (r(sK2,sK0(sK2),sK2,sK1(sK2)) => s(sK2)), inference(instantiate, [status(thm)], [a2])).

fof(f3, plain, s(sK2), inference(modus_ponens, [status(thm)], [f2, f1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [s3, f3])).

% SZS output end Proof