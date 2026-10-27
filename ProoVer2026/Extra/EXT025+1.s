%------------------------------------------------------------------------------
% File     : EXT025+1.s : ProoVer 2026 (extra test)
% Proof    : Problems/EXT025+1.p
% Test     : reflexivity/status_cth - cth is reserved for the negated conjecture
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/EXT025+1.p',a1)).

fof(c, conjecture, f(a) = f(a), file('Problems/EXT025+1.p',c)).

fof(negc, negated_conjecture, ~(f(a) = f(a)), inference(negated_conjecture, [status(cth)], [c])).

fof(s, plain, f(a) = f(a), inference(reflexivity, [status(cth)], [a1])).

fof(bot, plain, $false, inference(consequence, [status(thm)], [negc, s])).

% SZS output end Proof
