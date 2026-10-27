%------------------------------------------------------------------------------
% File     : EXT076+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT076+1.p
% Test     : double_negation/wrong_atom - ~~q(a) does not follow from p(a)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT076+1.p',a1)).

fof(c, conjecture, ~~q(a), file('Problems/EXT076+1.p',c)).

fof(negc, negated_conjecture, ~(~~q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ~~q(a), inference(double_negation, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
