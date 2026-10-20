%------------------------------------------------------------------------------
% File     : EXT070+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT070+1.p
% Test     : conjunction/swapped_order - Sound conclusion q & p with the operands in the other order; strict operand order may reject it
% Expected : EDGE
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT070+1.p',a1)).

fof(a2, axiom, q(a), file('Problems/EXT070+1.p',a2)).

fof(c, conjecture, q(a) & p(a), file('Problems/EXT070+1.p',c)).

fof(negc, negated_conjecture, ~(q(a) & p(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, q(a) & p(a), inference(conjunction, [status(thm)], [a1, a2])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
