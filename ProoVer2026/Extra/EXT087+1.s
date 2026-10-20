%------------------------------------------------------------------------------
% File     : EXT087+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT087+1.p
% Test     : rename_variable/swapped_arguments - Renaming also swaps the arguments
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: ?[Y]: r(X,Y), file('Problems/EXT087+1.p',a1)).

fof(c, conjecture, ![U]: ?[V]: r(V,U), file('Problems/EXT087+1.p',c)).

fof(negc, negated_conjecture, ~(![U]: ?[V]: r(V,U)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ![U]: ?[V]: r(V,U), inference(rename_variable, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
