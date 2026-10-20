%------------------------------------------------------------------------------
% File     : EXT077+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT077+1.p
% Test     : remove_double_negation/base - ~~p |- p
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ~~p(a), file('Problems/EXT077+1.p',a1)).

fof(a2, axiom, ~p(a), file('Problems/EXT077+1.p',a2)).

fof(c, conjecture, p(a), file('Problems/EXT077+1.p',c)).

fof(negc, negated_conjecture, ~(p(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, p(a), inference(remove_double_negation, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
