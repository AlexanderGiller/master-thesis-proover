%------------------------------------------------------------------------------
% File     : EXT045+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT045+1.p
% Test     : excluded_middle/different_atoms - q(a) | ~r(a) is not a tautology
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT045+1.p',a1)).

fof(c, conjecture, q(a) | ~r(a), file('Problems/EXT045+1.p',c)).

fof(negc, negated_conjecture, ~(q(a) | ~r(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a) | ~r(a), inference(excluded_middle, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
