%------------------------------------------------------------------------------
% File     : EXT088+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT088+1.p
% Test     : rename_variable/variable_capture - Both variables renamed to the same name (capture)
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: ?[Y]: r(X,Y), file('Problems/EXT088+1.p',a1)).

fof(c, conjecture, ![Y]: ?[Y]: r(Y,Y), file('Problems/EXT088+1.p',c)).

fof(negc, negated_conjecture, ~(![Y]: ?[Y]: r(Y,Y)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ![Y]: ?[Y]: r(Y,Y), inference(rename_variable, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
