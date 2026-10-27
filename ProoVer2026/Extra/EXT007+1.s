%------------------------------------------------------------------------------
% File     : EXT007+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT007+1.p
% Test     : resolution/ground - Ground resolution
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a) | q(a), file('Problems/EXT007+1.p',a1)).

fof(a2, axiom, ~p(a) | r(a), file('Problems/EXT007+1.p',a2)).

fof(c, conjecture, q(a) | r(a), file('Problems/EXT007+1.p',c)).

fof(negc, negated_conjecture, ~(q(a) | r(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a) | r(a), inference(resolution, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
