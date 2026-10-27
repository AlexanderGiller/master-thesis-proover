%------------------------------------------------------------------------------
% File     : EXT049+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT049+1.p
% Test     : existential_gen/base - p(a) |- ?X p(X)
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT049+1.p',a1)).

fof(c, conjecture, ?[X]: p(X), file('Problems/EXT049+1.p',c)).

fof(negc, negated_conjecture, ~(?[X]: p(X)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ?[X]: p(X), inference(existential_gen, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
