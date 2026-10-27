%------------------------------------------------------------------------------
% File     : EXT081+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT081+1.p
% Test     : copy/changed_formula - Copy changes p(a) to q(a)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT081+1.p',a1)).

fof(c, conjecture, q(a), file('Problems/EXT081+1.p',c)).

fof(negc, negated_conjecture, ~(q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a), inference(copy, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
