%------------------------------------------------------------------------------
% File     : EXT092+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT092+1.p
% Test     : resolution/wrong_unifier - Resolvent uses X := b instead of the unifier X := a
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) | q(X)), file('Problems/EXT092+1.p',a1)).

fof(a2, axiom, ~p(a) | r(a), file('Problems/EXT092+1.p',a2)).

fof(c, conjecture, q(b) | r(a), file('Problems/EXT092+1.p',c)).

fof(negc, negated_conjecture, ~(q(b) | r(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(b) | r(a), inference(resolution, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
