%------------------------------------------------------------------------------
% File     : EXT098+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT098+1.p
% Test     : paramodulation/target_needs_instantiation - Sound (superposition unifies X := a in the target), but the target variable is not instantiated by a one-sided matcher
% Expected : EDGE
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: p(f(X)), file('Problems/EXT098+1.p',a1)).

fof(a2, axiom, f(a) = c, file('Problems/EXT098+1.p',a2)).

fof(c, conjecture, p(c), file('Problems/EXT098+1.p',c)).

fof(negc, negated_conjecture, ~(p(c)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(c), inference(paramodulation, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
