%------------------------------------------------------------------------------
% File     : EXT066+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT066+1.p
% Test     : modus_ponens/universal_wrong_instance - q(b) does not follow from p(a)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) => q(X)), file('Problems/EXT066+1.p',a1)).

fof(a2, axiom, p(a), file('Problems/EXT066+1.p',a2)).

fof(c, conjecture, q(b), file('Problems/EXT066+1.p',c)).

fof(negc, negated_conjecture, ~(q(b)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(b), inference(modus_ponens, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
