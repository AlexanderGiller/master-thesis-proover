%------------------------------------------------------------------------------
% A simple FOF problem: Everyone who is mortal dies. Socrates is mortal.
% Conjecture: Socrates dies.
%------------------------------------------------------------------------------
fof(ax1, axiom, ! [X] : (mortal(X) => dies(X))).
fof(ax2, axiom, mortal(socrates)).
fof(con, conjecture, dies(socrates)).