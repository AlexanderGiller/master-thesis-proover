%------------------------------------------------------------------------------
% File     : EXT041+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT041+1.p
% Test     : commute/conjunction_three_operands - Extra operand added while swapping
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a) & q(a), file('Problems/EXT041+1.p',a1)).

fof(c, conjecture, q(a) & p(a) & r(a), file('Problems/EXT041+1.p',c)).

fof(negc, negated_conjecture, ~(q(a) & p(a) & r(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a) & p(a) & r(a), inference(commute, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
