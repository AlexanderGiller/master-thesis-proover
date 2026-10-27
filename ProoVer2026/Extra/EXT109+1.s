%------------------------------------------------------------------------------
% File     : EXT109+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT109+1.p
% Test     : consequence/bot_unrelated - Final $false uses an unrelated derived step (r(a)) instead of the proof of the conjecture
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a) => q(a), file('Problems/EXT109+1.p',a1)).

fof(a2, axiom, p(a), file('Problems/EXT109+1.p',a2)).

fof(c, conjecture, q(a), file('Problems/EXT109+1.p',c)).

fof(negc, negated_conjecture, ~(q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a), inference(modus_ponens, [status(thm)], [a1, a2])).

fof(t, plain, r(a), inference(modus_ponens, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, t])).

% SZS output end Proof
