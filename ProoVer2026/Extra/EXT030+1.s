%------------------------------------------------------------------------------
% File     : EXT030+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT030+1.p
% Test     : transitivity/status_cth - cth is reserved for the negated conjecture
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, a = b, file('Problems/EXT030+1.p',a1)).

fof(a2, axiom, b = c, file('Problems/EXT030+1.p',a2)).

fof(a3, axiom, d = e, file('Problems/EXT030+1.p',a3)).

fof(c, conjecture, a = c, file('Problems/EXT030+1.p',c)).

fof(negc, negated_conjecture, ~(a = c), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, a = c, inference(transitivity, [status(cth)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
