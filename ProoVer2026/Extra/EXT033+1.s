%------------------------------------------------------------------------------
% File     : EXT033+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT033+1.p
% Test     : rewrite/unrelated_conclusion - Conclusion q(a) does not follow from the parent
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT033+1.p',a1)).

fof(a2, axiom, a = b, file('Problems/EXT033+1.p',a2)).

fof(c, conjecture, q(a), file('Problems/EXT033+1.p',c)).

fof(negc, negated_conjecture, ~(q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a), inference(rewrite, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
