%------------------------------------------------------------------------------
% File     : EXT084+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT084+1.p
% Test     : duplicate/different_parents - Parents p(a) and q(a) differ
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT084+1.p',a1)).

fof(a2, axiom, q(a), file('Problems/EXT084+1.p',a2)).

fof(c, conjecture, p(a), file('Problems/EXT084+1.p',c)).

fof(negc, negated_conjecture, ~(p(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(a), inference(duplicate, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
