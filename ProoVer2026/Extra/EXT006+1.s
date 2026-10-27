%------------------------------------------------------------------------------
% File     : EXT006+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT006+1.p
% Test     : resolution/missing_parent - Second parent does not exist
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) | q(X)), file('Problems/EXT006+1.p',a1)).

fof(a2, axiom, ![X]: (~p(X) | r(X)), file('Problems/EXT006+1.p',a2)).

fof(a3, axiom, ![X]: (u(X) | r(X)), file('Problems/EXT006+1.p',a3)).

fof(c, conjecture, ![X]: (q(X) | r(X)), file('Problems/EXT006+1.p',c)).

fof(negc, negated_conjecture, ~(![X]: (q(X) | r(X))), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, ![X]: (q(X) | r(X)), inference(resolution, [status(thm)], [a1, zz])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
