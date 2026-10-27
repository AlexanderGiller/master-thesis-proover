%------------------------------------------------------------------------------
% File     : EXT063+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT063+1.p
% Test     : modus_ponens/wrong_conclusion - r(a) does not follow
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a) => q(a), file('Problems/EXT063+1.p',a1)).

fof(a2, axiom, p(a), file('Problems/EXT063+1.p',a2)).

fof(a3, axiom, q(a), file('Problems/EXT063+1.p',a3)).

fof(c, conjecture, r(a), file('Problems/EXT063+1.p',c)).

fof(negc, negated_conjecture, ~(r(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, r(a), inference(modus_ponens, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
