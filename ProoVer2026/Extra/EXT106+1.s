%------------------------------------------------------------------------------
% File     : EXT106+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT106+1.p
% Test     : transitivity/shared_right_term - a=b, c=b |- a=c (common term on the right)
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, a = b, file('Problems/EXT106+1.p',a1)).

fof(a2, axiom, c = b, file('Problems/EXT106+1.p',a2)).

fof(c, conjecture, a = c, file('Problems/EXT106+1.p',c)).

fof(negc, negated_conjecture, ~(a = c), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, a = c, inference(transitivity, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
