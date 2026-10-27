%------------------------------------------------------------------------------
% File     : EXT038+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT038+1.p
% Test     : weaken/new_disjunct_first - Sound weakening with the new disjunct in front; a strict prefix check may reject it
% Expected : EDGE
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT038+1.p',a1)).

fof(c, conjecture, q(a) | p(a), file('Problems/EXT038+1.p',c)).

fof(negc, negated_conjecture, ~(q(a) | p(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a) | p(a), inference(weaken, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
