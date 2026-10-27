%------------------------------------------------------------------------------
% File     : EXT022+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT022+1.p
% Test     : reflexivity/not_reflexive - Conclusion f(a) = f(b) is not reflexive
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT022+1.p',a1)).

fof(c, conjecture, f(a) = f(b), file('Problems/EXT022+1.p',c)).

fof(negc, negated_conjecture, ~(f(a) = f(b)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, f(a) = f(b), inference(reflexivity, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
