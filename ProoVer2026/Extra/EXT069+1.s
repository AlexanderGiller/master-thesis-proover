%------------------------------------------------------------------------------
% File     : EXT069+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT069+1.p
% Test     : conjunction/single_parent_repeated - q(a) is not derivable from the single parent p(a)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT069+1.p',a1)).

fof(a2, axiom, q(a), file('Problems/EXT069+1.p',a2)).

fof(c, conjecture, p(a) & q(a), file('Problems/EXT069+1.p',c)).

fof(negc, negated_conjecture, ~(p(a) & q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(a) & q(a), inference(conjunction, [status(thm)], [a1, a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
