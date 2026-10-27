%------------------------------------------------------------------------------
% File     : EXT013+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT013+1.p
% Test     : paramodulation/wrong_predicate - Predicate changed from p to q during rewriting
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(f(a)), file('Problems/EXT013+1.p',a1)).

fof(a2, axiom, ![X]: f(X) = g(X), file('Problems/EXT013+1.p',a2)).

fof(a3, axiom, ![X]: f(X) = h(X), file('Problems/EXT013+1.p',a3)).

fof(c, conjecture, q(g(a)), file('Problems/EXT013+1.p',c)).

fof(negc, negated_conjecture, ~(q(g(a))), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(g(a)), inference(paramodulation, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
