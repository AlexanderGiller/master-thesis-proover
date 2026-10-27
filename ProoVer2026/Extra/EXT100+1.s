%------------------------------------------------------------------------------
% File     : EXT100+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT100+1.p
% Test     : instantiate/variable_capture - Instantiating X := Y would be captured by ?[Y]
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: ?[Y]: r(X,Y), file('Problems/EXT100+1.p',a1)).

fof(c, conjecture, ?[Y]: r(Y,Y), file('Problems/EXT100+1.p',c)).

fof(negc, negated_conjecture, ~(?[Y]: r(Y,Y)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ?[Y]: r(Y,Y), inference(instantiate, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
