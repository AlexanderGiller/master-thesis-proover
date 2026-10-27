%------------------------------------------------------------------------------
% File     : EXT023+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT023+1.p
% Test     : reflexivity/negated_equality - Conclusion f(a) != f(a) is false
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT023+1.p',a1)).

fof(c, conjecture, f(a) != f(a), file('Problems/EXT023+1.p',c)).

fof(negc, negated_conjecture, ~(f(a) != f(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, f(a) != f(a), inference(reflexivity, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
