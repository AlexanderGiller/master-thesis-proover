%------------------------------------------------------------------------------
% File     : EXT073+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT073+1.p
% Test     : split_conjunct/parent_is_disjunction - Parent is p | q, from which q does not follow
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a) & q(a), file('Problems/EXT073+1.p',a1)).

fof(a2, axiom, p(a) | q(a), file('Problems/EXT073+1.p',a2)).

fof(c, conjecture, q(a), file('Problems/EXT073+1.p',c)).

fof(negc, negated_conjecture, ~(q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a), inference(split_conjunct, [status(thm)], [a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
