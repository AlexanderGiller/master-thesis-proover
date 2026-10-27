%------------------------------------------------------------------------------
% File     : EXT101+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT101+1.p
% Test     : modus_ponens/repeated_variable - Both occurrences of X receive the same instance
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) => q(X,X)), file('Problems/EXT101+1.p',a1)).

fof(a2, axiom, p(a), file('Problems/EXT101+1.p',a2)).

fof(c, conjecture, q(a,a), file('Problems/EXT101+1.p',c)).

fof(negc, negated_conjecture, ~(q(a,a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a,a), inference(modus_ponens, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
