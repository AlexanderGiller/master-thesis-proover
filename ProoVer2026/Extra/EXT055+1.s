%------------------------------------------------------------------------------
% File     : EXT055+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT055+1.p
% Test     : instantiate/base - !X p(X) |- p(a)
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: p(X), file('Problems/EXT055+1.p',a1)).

fof(c, conjecture, p(a), file('Problems/EXT055+1.p',c)).

fof(negc, negated_conjecture, ~(p(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(a), inference(instantiate, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
