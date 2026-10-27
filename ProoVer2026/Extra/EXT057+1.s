%------------------------------------------------------------------------------
% File     : EXT057+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT057+1.p
% Test     : instantiate/partial - Instantiate one of two universal variables
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X,Y]: r(X,Y), file('Problems/EXT057+1.p',a1)).

fof(c, conjecture, ![Y]: r(a,Y), file('Problems/EXT057+1.p',c)).

fof(negc, negated_conjecture, ~(![Y]: r(a,Y)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ![Y]: r(a,Y), inference(instantiate, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
