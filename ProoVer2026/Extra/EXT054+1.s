%------------------------------------------------------------------------------
% File     : EXT054+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT054+1.p
% Test     : existential_gen/diagonal - ?X r(X,X) would need a = b
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, r(a, b), file('Problems/EXT054+1.p',a1)).

fof(c, conjecture, ?[X]: r(X,X), file('Problems/EXT054+1.p',c)).

fof(negc, negated_conjecture, ~(?[X]: r(X,X)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ?[X]: r(X,X), inference(existential_gen, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
