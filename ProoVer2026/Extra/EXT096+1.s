%------------------------------------------------------------------------------
% File     : EXT096+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT096+1.p
% Test     : paramodulation/reverse_orientation - Equation used right to left
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(g(a)), file('Problems/EXT096+1.p',a1)).

fof(a2, axiom, ![X]: f(X) = g(X), file('Problems/EXT096+1.p',a2)).

fof(c, conjecture, p(f(a)), file('Problems/EXT096+1.p',c)).

fof(negc, negated_conjecture, ~(p(f(a))), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(f(a)), inference(paramodulation, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
