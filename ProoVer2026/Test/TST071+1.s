%------------------------------------------------------------------------------
% File     : TST071+1.s : ProoVer 2026
% Proof    : Problems/TST071+1.p
% Test     : cp03_inconsistent_axioms_without_negc - Edge: Axiome widerspruechlich, $false ohne negierte Konjunktur (Regeln fordern Refutation der Konjunktur?)
% Expected : EDGE
%------------------------------------------------------------------------------
% SZS output start Proof
fof(a1, axiom, p(a), file('Problems/TST071+1.p', a1)).

fof(a2, axiom, ~p(a), file('Problems/TST071+1.p', a2)).

fof(c1, conjecture, q(a), file('Problems/TST071+1.p', c1)).

fof(bot, plain, $false, inference(consequence, [status(thm)], [a1, a2])).

% SZS output end Proof