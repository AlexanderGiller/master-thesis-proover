%------------------------------------------------------------------------------
% File     : EXT108+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT108+1.p
% Test     : commute/nested_operand - Swap with a compound operand
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, (p(a) | q(a)) & r(a), file('Problems/EXT108+1.p',a1)).

fof(c, conjecture, r(a) & (p(a) | q(a)), file('Problems/EXT108+1.p',c)).

fof(negc, negated_conjecture, ~(r(a) & (p(a) | q(a))), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, r(a) & (p(a) | q(a)), inference(commute, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
