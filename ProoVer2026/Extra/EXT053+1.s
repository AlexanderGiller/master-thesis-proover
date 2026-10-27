%------------------------------------------------------------------------------
% File     : EXT053+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT053+1.p
% Test     : existential_gen/two_variables - r(a,b) |- ?X,Y r(X,Y)
% Expected : CORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, r(a, b), file('Problems/EXT053+1.p',a1)).

fof(c, conjecture, ?[X,Y]: r(X,Y), file('Problems/EXT053+1.p',c)).

fof(negc, negated_conjecture, ~(?[X,Y]: r(X,Y)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ?[X,Y]: r(X,Y), inference(existential_gen, [status(thm)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
