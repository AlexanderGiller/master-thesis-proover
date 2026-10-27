%------------------------------------------------------------------------------
% File     : EXT102+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT102+1.p
% Test     : modus_ponens/inconsistent_instance - q(a,b) uses different instances for the two occurrences of X
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) => q(X,X)), file('Problems/EXT102+1.p',a1)).

fof(a2, axiom, p(a), file('Problems/EXT102+1.p',a2)).

fof(c, conjecture, q(a,b), file('Problems/EXT102+1.p',c)).

fof(negc, negated_conjecture, ~(q(a,b)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a,b), inference(modus_ponens, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
