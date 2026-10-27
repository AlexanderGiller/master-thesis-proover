%------------------------------------------------------------------------------
% File     : TST045+1.s : ProoVer 2026
% Proof    : Problems/TST045+1.p
% Test     : st10_no_inference_record - plain-Formel ohne inference-Annotation
% Expected : INCORRECT
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, ![X]: (p(X) => q(X)), file('Problems/TST045+1.p', a1)).

fof(a2, axiom, p(a), file('Problems/TST045+1.p', a2)).

fof(c1, conjecture, q(a), file('Problems/TST045+1.p', c1)).

fof(nc1, negated_conjecture, ~q(a), inference(negated_conjecture, [status(cth)], [c1])).

fof(f1, plain, q(a)).

fof(f2, plain, $false, inference(consequence, [status(thm)], [f1, nc1])).

% SZS output end Proof