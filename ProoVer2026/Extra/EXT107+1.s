%------------------------------------------------------------------------------
% File     : EXT107+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT107+1.p
% Test     : weaken/two_new_disjuncts - Two disjuncts added at once
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT107+1.p',a1)).

fof(c, conjecture, p(a) | q(a) | r(a), file('Problems/EXT107+1.p',c)).

fof(negc, negated_conjecture, ~(p(a) | q(a) | r(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(a) | q(a) | r(a), inference(weaken, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
