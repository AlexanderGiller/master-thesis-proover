%------------------------------------------------------------------------------
% File     : TST058+1.s : ProoVer 2026
% Proof    : Problems/TST058+1.p
% Test     : sk19_symbol_clash_with_problem - Skolem-Symbol 'a' kollidiert mit Konstante a aus Axiom a3 - fuehrt zu unsoundem $false
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ?[X]: p(X), file('Problems/TST058+1.p', a1)).

fof(a2, axiom, ![X]: (p(X) => q(X)), file('Problems/TST058+1.p', a2)).

fof(a3, axiom, ~q(a), file('Problems/TST058+1.p', a3)).

fof(c1, conjecture, ?[X]: q(X), file('Problems/TST058+1.p', c1)).

fof(nc1, negated_conjecture, ~?[X]: q(X), inference(negated_conjecture, [status(cth)], [c1])).

fof(s1, plain, p(a), inference(skolemize, [status(esa), new_symbols(skolem, [a]), skolemize(X, a)], [a1])).

fof(f1, plain, q(a), inference(modus_ponens, [status(thm)], [a2, s1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [f1, a3])).

% SZS output end Proof