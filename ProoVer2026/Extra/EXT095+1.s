%------------------------------------------------------------------------------
% File     : EXT095+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT095+1.p
% Test     : resolution/occurs_check - p(X,X) and p(Y,f(Y)) are not unifiable (occurs check)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X, X) | q(X)), file('Problems/EXT095+1.p',a1)).

fof(a2, axiom, ![Y]: (~p(Y, f(Y)) | r(Y)), file('Problems/EXT095+1.p',a2)).

fof(c, conjecture, ![X]: (q(X) | r(X)), file('Problems/EXT095+1.p',c)).

fof(negc, negated_conjecture, ~(![X]: (q(X) | r(X))), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ![X]: (q(X) | r(X)), inference(resolution, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
