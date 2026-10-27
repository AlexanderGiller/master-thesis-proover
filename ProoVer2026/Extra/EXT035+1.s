%------------------------------------------------------------------------------
% File     : EXT035+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT035+1.p
% Test     : weaken/not_a_disjunction - Conclusion p(a) & q(a) is stronger than the parent
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT035+1.p',a1)).

fof(c, conjecture, p(a) & q(a), file('Problems/EXT035+1.p',c)).

fof(negc, negated_conjecture, ~(p(a) & q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(a) & q(a), inference(weaken, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
