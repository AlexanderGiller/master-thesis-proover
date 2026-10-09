%------------------------------------------------------------------------------
% File     : TST048+1.s : ProoVer 2026
% Proof    : Problems/TST048+1.p
% Test     : c09_skolem_inside_conjunction - Skolemisierung eines Existenzquantors tief in einer Konjunktion (positive Polaritaet)
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, (p(a) & ?[X]: q(X)), file('Problems/TST048+1.p', a1)).

fof(c1, conjecture, ?[X]: q(X), file('Problems/TST048+1.p', c1)).

fof(nc1, negated_conjecture, ~?[X]: q(X), inference(negated_conjecture, [status(cth)], [c1])).

fof(s1, plain, (p(a) & q(sK0)), inference(skolemize, [status(esa), new_symbols(skolem, [sK0]), skolemize(X, sK0)], [a1])).

fof(f1, plain, q(sK0), inference(split_conjunct, [status(thm)], [s1])).

fof(f2, plain, ~q(sK0), inference(instantiate, [status(thm)], [nc1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [f1, f2])).

% SZS output end Proof