%------------------------------------------------------------------------------
% File     : EXT052+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT052+1.p
% Test     : existential_gen/no_quantifier - No existential quantifier introduced; the term is replaced by b
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT052+1.p',a1)).

fof(c, conjecture, p(b), file('Problems/EXT052+1.p',c)).

fof(negc, negated_conjecture, ~(p(b)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(b), inference(existential_gen, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
