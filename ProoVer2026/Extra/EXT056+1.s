%------------------------------------------------------------------------------
% File     : EXT056+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT056+1.p
% Test     : instantiate/wrong_predicate - q(a) does not follow from !X p(X)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: p(X), file('Problems/EXT056+1.p',a1)).

fof(c, conjecture, q(a), file('Problems/EXT056+1.p',c)).

fof(negc, negated_conjecture, ~(q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a), inference(instantiate, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
