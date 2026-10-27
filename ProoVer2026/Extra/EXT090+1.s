%------------------------------------------------------------------------------
% File     : EXT090+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT090+1.p
% Test     : add_hypothesis/wrong_consequent - q => r does not follow from p
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT090+1.p',a1)).

fof(c, conjecture, q(a) => r(a), file('Problems/EXT090+1.p',c)).

fof(negc, negated_conjecture, ~(q(a) => r(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a) => r(a), inference(add_hypothesis, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
