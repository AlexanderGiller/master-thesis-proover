%------------------------------------------------------------------------------
% File     : EXT014+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT014+1.p
% Test     : paramodulation/wrong_equation - Equation used is f(X)=h(X) but the conclusion contains g(a)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(f(a)), file('Problems/EXT014+1.p',a1)).

fof(a2, axiom, ![X]: f(X) = g(X), file('Problems/EXT014+1.p',a2)).

fof(a3, axiom, ![X]: f(X) = h(X), file('Problems/EXT014+1.p',a3)).

fof(c, conjecture, p(g(a)), file('Problems/EXT014+1.p',c)).

fof(negc, negated_conjecture, ~(p(g(a))), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(g(a)), inference(paramodulation, [status(thm)], [a1, a3])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
