%------------------------------------------------------------------------------
% Problem requiring Skolemization.
% There exists someone who is mortal. Conjecture: someone dies.
%------------------------------------------------------------------------------
fof(ax1, axiom, ?[X] : mortal(X)).
fof(ax2, axiom, ![X] : (mortal(X) => dies(X))).
fof(con, conjecture, ?[Y] : dies(Y)).