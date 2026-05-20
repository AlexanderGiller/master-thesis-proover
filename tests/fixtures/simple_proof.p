%------------------------------------------------------------------------------
% Proof: simple.p
%------------------------------------------------------------------------------
fof(ax1, axiom, ![X] : (mortal(X) => dies(X)),
    file('tests/fixtures/simple.p', ax1)).
fof(ax2, axiom, mortal(socrates),
    file('tests/fixtures/simple.p', ax2)).
fof(con, conjecture, dies(socrates),
    file('tests/fixtures/simple.p', con)).
fof(neg_con, negated_conjecture, ~dies(socrates),
    inference(negate_conjecture, [status(thm)], [con])).
fof(inst1, plain, (mortal(socrates) => dies(socrates)),
    inference(resolution, [status(thm)], [ax1])).
fof(mp1, plain, dies(socrates),
    inference(resolution, [status(thm)], [inst1, ax2])).
fof(contra, plain, $false,
    inference(resolution, [status(thm)], [mp1, neg_con])).