%------------------------------------------------------------------------------
% Simple FOF problem: Socrates is mortal, all mortals die.
% Conjecture: Socrates dies.
%------------------------------------------------------------------------------
fof(ax1, axiom, ![X] : (mortal(X) => dies(X))).
fof(ax2, axiom, mortal(socrates)).
fof(con, conjecture, dies(socrates)).