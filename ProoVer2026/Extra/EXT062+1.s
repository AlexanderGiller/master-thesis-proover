%------------------------------------------------------------------------------
% File     : EXT062+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT062+1.p
% Test     : modus_ponens/affirming_consequent - p => q, q |- p is unsound
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a) => q(a), file('Problems/EXT062+1.p',a1)).

fof(a2, axiom, p(a), file('Problems/EXT062+1.p',a2)).

fof(a3, axiom, q(a), file('Problems/EXT062+1.p',a3)).

fof(c, conjecture, p(a), file('Problems/EXT062+1.p',c)).

fof(negc, negated_conjecture, ~(p(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(a), inference(modus_ponens, [status(thm)], [a1, a3])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
