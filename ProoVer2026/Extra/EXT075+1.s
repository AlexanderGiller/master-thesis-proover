%------------------------------------------------------------------------------
% File     : EXT075+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT075+1.p
% Test     : double_negation/single_negation - ~p(a) is the negation, not a double negation
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT075+1.p',a1)).

fof(c, conjecture, ~p(a), file('Problems/EXT075+1.p',c)).

fof(negc, negated_conjecture, ~(~p(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ~p(a), inference(double_negation, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
