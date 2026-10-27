%------------------------------------------------------------------------------
% File     : TST060+1.s : ProoVer 2026
% Proof    : Problems/TST060+1.p
% Test     : sk21_two_variables_in_one_step - ?[X]?[Y] in einem Schritt eliminiert, aber nur ein Symbol/eine Variable angegeben
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ?[X]: ?[Y]: r(X,Y), file('Problems/TST060+1.p', a1)).

fof(a2, axiom, ![X]: ![Y]: (r(X,Y) => s), file('Problems/TST060+1.p', a2)).

fof(c1, conjecture, s, file('Problems/TST060+1.p', c1)).

fof(nc1, negated_conjecture, ~s, inference(negated_conjecture, [status(cth)], [c1])).

fof(s2, plain, r(sK0,sK1), inference(skolemize, [status(esa), new_symbols(skolem, [sK0]), skolemize(X, sK0)], [a1])).

fof(f1, plain, (r(sK0,sK1) => s), inference(instantiate, [status(thm)], [a2])).

fof(f2, plain, s, inference(modus_ponens, [status(thm)], [f1, s2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [nc1, f2])).

% SZS output end Proof