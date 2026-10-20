%------------------------------------------------------------------------------
% File     : EXT071+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT071+1.p
% Test     : split_conjunct/base - p & q |- q
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a) & q(a), file('Problems/EXT071+1.p',a1)).

fof(a2, axiom, p(a) | q(a), file('Problems/EXT071+1.p',a2)).

fof(c, conjecture, q(a), file('Problems/EXT071+1.p',c)).

fof(negc, negated_conjecture, ~(q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a), inference(split_conjunct, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
