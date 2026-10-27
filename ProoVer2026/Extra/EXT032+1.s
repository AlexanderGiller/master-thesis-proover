%------------------------------------------------------------------------------
% File     : EXT032+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT032+1.p
% Test     : rewrite/unjustified_rewrite - p(a) rewritten to p(b) although the equation a=b is not cited as a parent
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT032+1.p',a1)).

fof(a2, axiom, a = b, file('Problems/EXT032+1.p',a2)).

fof(c, conjecture, p(b), file('Problems/EXT032+1.p',c)).

fof(negc, negated_conjecture, ~(p(b)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(b), inference(rewrite, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
