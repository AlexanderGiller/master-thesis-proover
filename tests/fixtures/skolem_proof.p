%------------------------------------------------------------------------------
% Proof: skolem.p
%------------------------------------------------------------------------------
fof(ax1, axiom, ?[X] : mortal(X),
    file('tests/fixtures/skolem.p', ax1)).
fof(ax1_sk, plain, mortal(sK0),
    inference(skolemize, [status(esa), new_symbols(skolem, [sK0]), skolemize(X, sK0)], [ax1])).
fof(ax2, axiom, ![X] : (mortal(X) => dies(X)),
    file('tests/fixtures/skolem.p', ax2)).
fof(con, conjecture, ?[Y] : dies(Y),
    file('tests/fixtures/skolem.p', con)).
fof(neg_con, negated_conjecture, ~(?[Y] : dies(Y)),
    inference(negate_conjecture, [status(thm)], [con])).
fof(neg_con_sk, plain, ~dies(sK1),
    inference(skolemize, [status(esa), new_symbols(skolem, [sK1]), skolemize(Y, sK1)], [neg_con])).
fof(inst1, plain, (mortal(sK0) => dies(sK0)),
    inference(resolution, [status(thm)], [ax2])).
fof(mp1, plain, dies(sK0),
    inference(resolution, [status(thm)], [inst1, ax1_sk])).
fof(contra, plain, $false,
    inference(resolution, [status(thm)], [mp1, neg_con_sk])).