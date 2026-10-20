%------------------------------------------------------------------------------
% File     : EXT003+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT003+1.p
% Test     : resolution/dropped_literal - Literal r(X) dropped from the resolvent (unsound)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) | q(X)), file('Problems/EXT003+1.p',a1)).

fof(a2, axiom, ![X]: (~p(X) | r(X)), file('Problems/EXT003+1.p',a2)).

fof(a3, axiom, ![X]: (u(X) | r(X)), file('Problems/EXT003+1.p',a3)).

fof(c, conjecture, ![X]: q(X), file('Problems/EXT003+1.p',c)).

fof(negc, negated_conjecture, ~(![X]: q(X)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ![X]: q(X), inference(resolution, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
