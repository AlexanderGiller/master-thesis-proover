%------------------------------------------------------------------------------
% File     : EXT085+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT085+1.p
% Test     : duplicate/changed_formula - Conclusion q(a) differs from the duplicated formula
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT085+1.p',a1)).

fof(a2, axiom, q(a), file('Problems/EXT085+1.p',a2)).

fof(c, conjecture, q(a), file('Problems/EXT085+1.p',c)).

fof(negc, negated_conjecture, ~(q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a), inference(duplicate, [status(thm)], [a1, a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
