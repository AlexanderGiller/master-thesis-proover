%------------------------------------------------------------------------------
% File     : EXT044+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT044+1.p
% Test     : excluded_middle/base - phi | ~phi
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT044+1.p',a1)).

fof(c, conjecture, q(a) | ~q(a), file('Problems/EXT044+1.p',c)).

fof(negc, negated_conjecture, ~(q(a) | ~q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a) | ~q(a), inference(excluded_middle, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
