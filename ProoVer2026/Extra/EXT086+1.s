%------------------------------------------------------------------------------
% File     : EXT086+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT086+1.p
% Test     : rename_variable/base - Consistent renaming of bound variables
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: ?[Y]: r(X,Y), file('Problems/EXT086+1.p',a1)).

fof(c, conjecture, ![U]: ?[V]: r(U,V), file('Problems/EXT086+1.p',c)).

fof(negc, negated_conjecture, ~(![U]: ?[V]: r(U,V)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ![U]: ?[V]: r(U,V), inference(rename_variable, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
