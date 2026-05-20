%------------------------------------------------------------------------------
% Proof: test001
% Proof: test001.p
%------------------------------------------------------------------------------

% Step 1: introduce the conjecture as-is
fof(con, conjecture, dies(socrates), file('Problems/test001.p', con)).

% Step 2: negate the conjecture (refutation proof)
fof(neg_con, negated_conjecture, ~dies(socrates),
    inference(negate_conjecture, [status(thm)], [con])).

% Step 3: copy axiom 1 from the problem
fof(ax1, axiom, ! [X] : (mortal(X) => dies(X)), file('Problems/test001.p', ax1)).

% Step 4: copy axiom 2 from the problem
fof(ax2, axiom, mortal(socrates), file('Problems/test001.p', ax2)).

% Step 5: instantiate ax1 with X = socrates → mortal(socrates) => dies(socrates)
fof(inst1, plain, (mortal(socrates) => dies(socrates)),
    inference(resolution, [status(thm)], [ax1])).

% Step 6: apply modus ponens using ax2 and inst1 → dies(socrates)
fof(mp1, plain, dies(socrates),
    inference(resolution, [status(thm)], [inst1, ax2])).

% Step 7: contradiction between mp1 and neg_con → $false
fof(contra, plain, $false,
    inference(resolution, [status(thm)], [mp1, neg_con])).