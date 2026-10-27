%------------------------------------------------------------------------------
% File     : EXT042+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT042+1.p
% Test     : commute/disjunction - Swap of the operands of a disjunction
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a) | q(a), file('Problems/EXT042+1.p',a1)).

fof(c, conjecture, q(a) | p(a), file('Problems/EXT042+1.p',c)).

fof(negc, negated_conjecture, ~(q(a) | p(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a) | p(a), inference(commute, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
