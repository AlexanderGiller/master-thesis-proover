%------------------------------------------------------------------------------
% File     : EXT105+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT105+1.p
% Test     : reflexivity/quantified - Sound, but the conclusion is a quantified equation, not t = t
% Expected : EDGE
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT105+1.p',a1)).

fof(c, conjecture, ![X]: X = X, file('Problems/EXT105+1.p',c)).

fof(negc, negated_conjecture, ~(![X]: X = X), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ![X]: X = X, inference(reflexivity, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
