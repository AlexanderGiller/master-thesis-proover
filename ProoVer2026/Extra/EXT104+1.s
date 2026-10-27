%------------------------------------------------------------------------------
% File     : EXT104+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT104+1.p
% Test     : excluded_middle/quantified - Sound tautology below a universal quantifier; the rule's shape check expects a top-level disjunction
% Expected : EDGE
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT104+1.p',a1)).

fof(c, conjecture, ![X]: (q(X) | ~q(X)), file('Problems/EXT104+1.p',c)).

fof(negc, negated_conjecture, ~(![X]: (q(X) | ~q(X))), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ![X]: (q(X) | ~q(X)), inference(excluded_middle, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
