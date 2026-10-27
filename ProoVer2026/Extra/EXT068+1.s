%------------------------------------------------------------------------------
% File     : EXT068+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT068+1.p
% Test     : conjunction/unsupported_operand - r(a) is not among the parents
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT068+1.p',a1)).

fof(a2, axiom, q(a), file('Problems/EXT068+1.p',a2)).

fof(c, conjecture, p(a) & r(a), file('Problems/EXT068+1.p',c)).

fof(negc, negated_conjecture, ~(p(a) & r(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(a) & r(a), inference(conjunction, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
