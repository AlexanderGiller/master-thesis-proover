%------------------------------------------------------------------------------
% File     : EXT046+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT046+1.p
% Test     : excluded_middle/no_negation - q(a) | q(a) is not a tautology
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT046+1.p',a1)).

fof(c, conjecture, q(a) | q(a), file('Problems/EXT046+1.p',c)).

fof(negc, negated_conjecture, ~(q(a) | q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a) | q(a), inference(excluded_middle, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
