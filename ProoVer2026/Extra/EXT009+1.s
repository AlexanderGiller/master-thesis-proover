%------------------------------------------------------------------------------
% File     : EXT009+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT009+1.p
% Test     : resolution/swapped_literal_order - Sound resolvent with the literals in the other order; a strict syntactic matcher may reject it
% Expected : EDGE
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a) | q(a), file('Problems/EXT009+1.p',a1)).

fof(a2, axiom, ~p(a) | r(a), file('Problems/EXT009+1.p',a2)).

fof(c, conjecture, r(a) | q(a), file('Problems/EXT009+1.p',c)).

fof(negc, negated_conjecture, ~(r(a) | q(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, r(a) | q(a), inference(resolution, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
