%------------------------------------------------------------------------------
% File     : EXT059+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT059+1.p
% Test     : instantiate/inconsistent_instance - Occurrences of X replaced by different terms
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: r(X,X), file('Problems/EXT059+1.p',a1)).

fof(c, conjecture, r(a,b), file('Problems/EXT059+1.p',c)).

fof(negc, negated_conjecture, ~(r(a,b)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, r(a,b), inference(instantiate, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
