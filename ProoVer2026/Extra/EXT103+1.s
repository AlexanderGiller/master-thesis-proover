%------------------------------------------------------------------------------
% File     : EXT103+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT103+1.p
% Test     : split_conjunct/below_quantifier - Sound, but the parent is a quantified conjunction, not a conjunction at top level
% Expected : EDGE
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) & q(X)), file('Problems/EXT103+1.p',a1)).

fof(c, conjecture, ![X]: q(X), file('Problems/EXT103+1.p',c)).

fof(negc, negated_conjecture, ~(![X]: q(X)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ![X]: q(X), inference(split_conjunct, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
