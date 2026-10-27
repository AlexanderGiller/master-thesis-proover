%------------------------------------------------------------------------------
% File     : EXT017+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT017+1.p
% Test     : paramodulation/under_quantifier - Rewrite below a universal quantifier
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![Y]: p(f(Y)), file('Problems/EXT017+1.p',a1)).

fof(a2, axiom, ![X]: f(X) = c, file('Problems/EXT017+1.p',a2)).

fof(c, conjecture, ![Y]: p(c), file('Problems/EXT017+1.p',c)).

fof(negc, negated_conjecture, ~(![Y]: p(c)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ![Y]: p(c), inference(paramodulation, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
