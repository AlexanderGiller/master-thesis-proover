%------------------------------------------------------------------------------
% File     : EXT050+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT050+1.p
% Test     : existential_gen/other_predicate - ?X q(X) does not follow from p(a)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT050+1.p',a1)).

fof(c, conjecture, ?[X]: q(X), file('Problems/EXT050+1.p',c)).

fof(negc, negated_conjecture, ~(?[X]: q(X)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ?[X]: q(X), inference(existential_gen, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
