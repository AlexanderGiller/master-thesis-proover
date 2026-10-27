%------------------------------------------------------------------------------
% File     : EXT093+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT093+1.p
% Test     : resolution/variables_standardised_apart - Both parents use X; the unifier is X1 := a, X2 := c
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X, c) | q(X)), file('Problems/EXT093+1.p',a1)).

fof(a2, axiom, ![X]: (~p(a, X) | r(X)), file('Problems/EXT093+1.p',a2)).

fof(c, conjecture, q(a) | r(c), file('Problems/EXT093+1.p',c)).

fof(negc, negated_conjecture, ~(q(a) | r(c)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a) | r(c), inference(resolution, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
