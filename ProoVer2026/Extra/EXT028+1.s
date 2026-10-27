%------------------------------------------------------------------------------
% File     : EXT028+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT028+1.p
% Test     : transitivity/no_common_term - Parents a=b and d=e share no term
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, a = b, file('Problems/EXT028+1.p',a1)).

fof(a2, axiom, b = c, file('Problems/EXT028+1.p',a2)).

fof(a3, axiom, d = e, file('Problems/EXT028+1.p',a3)).

fof(c, conjecture, a = e, file('Problems/EXT028+1.p',c)).

fof(negc, negated_conjecture, ~(a = e), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, a = e, inference(transitivity, [status(thm)], [a1, a3])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
