%------------------------------------------------------------------------------
% File     : EXT072+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT072+1.p
% Test     : split_conjunct/not_a_conjunct - r(a) is not a conjunct of the parent
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a) & q(a), file('Problems/EXT072+1.p',a1)).

fof(a2, axiom, p(a) | q(a), file('Problems/EXT072+1.p',a2)).

fof(c, conjecture, r(a), file('Problems/EXT072+1.p',c)).

fof(negc, negated_conjecture, ~(r(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, r(a), inference(split_conjunct, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
