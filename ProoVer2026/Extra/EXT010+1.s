%------------------------------------------------------------------------------
% File     : EXT010+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT010+1.p
% Test     : paramodulation/base - Rewrite f(a) to g(a) with an instance of a universally quantified equation
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(f(a)), file('Problems/EXT010+1.p',a1)).

fof(a2, axiom, ![X]: f(X) = g(X), file('Problems/EXT010+1.p',a2)).

fof(a3, axiom, ![X]: f(X) = h(X), file('Problems/EXT010+1.p',a3)).

fof(c, conjecture, p(g(a)), file('Problems/EXT010+1.p',c)).

fof(negc, negated_conjecture, ~(p(g(a))), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(g(a)), inference(paramodulation, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
