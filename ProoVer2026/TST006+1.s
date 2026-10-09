%------------------------------------------------------------------------------
% File     : TST006+1.s : ProoVer 2026
% Proof    : Problems/TST006+1.p
% Test     : c06_alpha_equivalence_renamed_steps - Axiome alpha-aequivalent (umbenannte Variablen) und andere Schrittnamen als in Problemdatei
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(ax_one, axiom, ![Y]: (p(Y) => q(Y)), file('Problems/TST006+1.p', a1)).

fof(ax_two, axiom, p(a), file('Problems/TST006+1.p', a2)).

fof(goal, conjecture, q(a), file('Problems/TST006+1.p', c1)).

fof(neg, negated_conjecture, ~q(a), inference(negated_conjecture, [status(cth)], [goal])).

fof(f1, plain, q(a), inference(modus_ponens, [status(thm)], [ax_one, ax_two])).

fof(f2, plain, $false, inference(consequence, [status(thm)], [f1, neg])).

% SZS output end Proof