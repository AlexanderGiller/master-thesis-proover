%------------------------------------------------------------------------------
% File     : EXT058+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT058+1.p
% Test     : instantiate/same_variable - Both occurrences get the same instance
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: r(X,X), file('Problems/EXT058+1.p',a1)).

fof(c, conjecture, r(a,a), file('Problems/EXT058+1.p',c)).

fof(negc, negated_conjecture, ~(r(a,a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, r(a,a), inference(instantiate, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
