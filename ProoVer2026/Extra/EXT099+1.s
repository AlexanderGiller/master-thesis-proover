%------------------------------------------------------------------------------
% File     : EXT099+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT099+1.p
% Test     : instantiate/under_existential - Instantiate X := a below the universal prefix
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: ?[Y]: r(X,Y), file('Problems/EXT099+1.p',a1)).

fof(c, conjecture, ?[Y]: r(a,Y), file('Problems/EXT099+1.p',c)).

fof(negc, negated_conjecture, ~(?[Y]: r(a,Y)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ?[Y]: r(a,Y), inference(instantiate, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
