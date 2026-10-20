%------------------------------------------------------------------------------
% File     : EXT024+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT024+1.p
% Test     : reflexivity/not_an_equation - Conclusion is p(a), not an equation
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT024+1.p',a1)).

fof(c, conjecture, p(a), file('Problems/EXT024+1.p',c)).

fof(negc, negated_conjecture, ~(p(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(a), inference(reflexivity, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
