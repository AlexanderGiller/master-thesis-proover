%------------------------------------------------------------------------------
% File     : EXT027+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT027+1.p
% Test     : transitivity/fresh_constant - Conclusion c = d relates a constant that is not chained
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, a = b, file('Problems/EXT027+1.p',a1)).

fof(a2, axiom, b = c, file('Problems/EXT027+1.p',a2)).

fof(a3, axiom, d = e, file('Problems/EXT027+1.p',a3)).

fof(c, conjecture, c = d, file('Problems/EXT027+1.p',c)).

fof(negc, negated_conjecture, ~(c = d), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, c = d, inference(transitivity, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
