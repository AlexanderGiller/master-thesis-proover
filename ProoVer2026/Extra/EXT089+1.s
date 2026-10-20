%------------------------------------------------------------------------------
% File     : EXT089+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT089+1.p
% Test     : add_hypothesis/base - p |- q => p
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT089+1.p',a1)).

fof(c, conjecture, q(a) => p(a), file('Problems/EXT089+1.p',c)).

fof(negc, negated_conjecture, ~(q(a) => p(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a) => p(a), inference(add_hypothesis, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
