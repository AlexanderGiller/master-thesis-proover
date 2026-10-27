%------------------------------------------------------------------------------
% File     : EXT097+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT097+1.p
% Test     : paramodulation/rewrites_all_occurrences - Sound, but two rewrite steps in one inference; a one-position check rejects it
% Expected : EDGE
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(f(a), f(a)), file('Problems/EXT097+1.p',a1)).

fof(a2, axiom, ![X]: f(X) = g(X), file('Problems/EXT097+1.p',a2)).

fof(c, conjecture, p(g(a), g(a)), file('Problems/EXT097+1.p',c)).

fof(negc, negated_conjecture, ~(p(g(a), g(a))), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(g(a), g(a)), inference(paramodulation, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
