%------------------------------------------------------------------------------
% File     : EXT011+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT011+1.p
% Test     : paramodulation/wrong_instance - Rewritten to g(b) instead of g(a)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(f(a)), file('Problems/EXT011+1.p',a1)).

fof(a2, axiom, ![X]: f(X) = g(X), file('Problems/EXT011+1.p',a2)).

fof(a3, axiom, ![X]: f(X) = h(X), file('Problems/EXT011+1.p',a3)).

fof(c, conjecture, p(g(b)), file('Problems/EXT011+1.p',c)).

fof(negc, negated_conjecture, ~(p(g(b))), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(g(b)), inference(paramodulation, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
