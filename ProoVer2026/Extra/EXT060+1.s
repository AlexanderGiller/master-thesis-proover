%------------------------------------------------------------------------------
% File     : EXT060+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT060+1.p
% Test     : instantiate/generalisation - Direction reversed: p(a) does not give !X p(X)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT060+1.p',a1)).

fof(c, conjecture, ![X]: p(X), file('Problems/EXT060+1.p',c)).

fof(negc, negated_conjecture, ~(![X]: p(X)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ![X]: p(X), inference(instantiate, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
