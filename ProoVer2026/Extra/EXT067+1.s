%------------------------------------------------------------------------------
% File     : EXT067+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT067+1.p
% Test     : conjunction/base - p, q |- p & q
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT067+1.p',a1)).

fof(a2, axiom, q(a), file('Problems/EXT067+1.p',a2)).

fof(c, conjecture, p(a) & q(a), file('Problems/EXT067+1.p',c)).

fof(negc, negated_conjecture, ~(p(a) & q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(a) & q(a), inference(conjunction, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
