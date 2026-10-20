%------------------------------------------------------------------------------
% File     : TST051+1.s : ProoVer 2026
% Proof    : Problems/TST051+1.p
% Test     : c12_negated_conjecture_equivalent_form - Edge: negierte Konjunktur als ![X]: ~q(X) (logisch aequivalent, nur per ATP/Normalisierung pruefbar)
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ?[X]: p(X), file('Problems/TST051+1.p', a1)).

fof(a2, axiom, ![X]: (p(X) => q(X)), file('Problems/TST051+1.p', a2)).

fof(c1, conjecture, ?[X]: q(X), file('Problems/TST051+1.p', c1)).

fof(nc1, negated_conjecture, ![X]: ~q(X), inference(negated_conjecture, [status(cth)], [c1])).

fof(s1, plain, p(sK0), inference(skolemize, [status(esa), new_symbols(skolem, [sK0]), skolemize(X, sK0)], [a1])).

fof(f1, plain, q(sK0), inference(modus_ponens, [status(thm)], [a2, s1])).

fof(f2, plain, ~q(sK0), inference(instantiate, [status(thm)], [nc1])).

fof(f3, plain, $false, inference(consequence, [status(thm)], [f1, f2])).

% SZS output end Proof