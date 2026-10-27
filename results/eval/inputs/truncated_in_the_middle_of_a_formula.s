%------------------------------------------------------------------------------
% File     : PRV010+1.s : ProoVer 2026
% Proof    : Problems/PRV010+1.p
%------------------------------------------------------------------------------
% SZS output start Proof
fof(s0,axiom,
    ! [X0,X2] :
    ? [X1] : t,
    file('Problems/PRV010+1.p',s0) ).

fof(s1,axiom,
    ! [X3] :
      ( X3 = a
    <=> ( t
        | q(f(X3)) ) ),
    file('Problems/PRV010+1.p',s1) ).

fof(s2,axiom,
    ! [X4] :
    ? [X5] : ~ q(c),
    file('Problems/PRV010+1.p',s2) ).

fof(s3,axiom,
    f(g(c,a)) = b,
    file('Problems/PRV010+1.p',s3) ).

fof(s4,axiom,
    ( ! [X6,X7] :
      ? [X8] : X7 = a
    & p(a) ),
    file('Problems/PRV010+1.p',s4) ).

fof(c,conjecture,
    ( ? [X22] : X22 = X22
    | ! [X23] :
      ? [X24] :
      ! [X25] :
      ? [X26] : q(a) ),
    file('Problems/PRV010+1.p',c) ).

fof(s5,plain,
    ( q(b)
    | ~ q(b) ),
    inference(excluded_middle,[status(thm)],[s2]) ).

fof(s6,plain,
    ~ ~ ( q(b)
        | ~ q(b) ),
    inference(double_negation,[status(thm)],[s5]) ).

fof(s7,plain,
    ? [X5] : ~ q(c),
    inference(instantiate,[status(thm)],[s2]) ).

fof(s8,plain,
    ( r(g(a,g(c,a)),f(f(c)))
   => ! [X4] :
      ? [X5] : ~ q(c) ),
    inference(add_hypothesis,[status(thm)],[s2]) ).

fof(s9,plain,
    ~ ~ ! [X0,X2] :
        ? [X1] : t,
    inference(double_negation,[status(thm)],[s0]) ).

fof(s10,plain,
    ? [X9] :
      ( q(X9)
      | ~ q(X9) ),
    inference(existential_gen,[status(thm)],[s5]) ).

fof(s11,plain,
    ! [X0,X2] :
    ? [X1] : t,
    inference(remove_double_negation,[status(thm)],[s9]) ).

fof(s12,plain,
    ? [X10] : f(g(X10,a)) = b,
    inference(existential_gen,[status(thm)],[s3]) ).

fof(s13,plain,
    ! [X2] :
    ? [X1] : t,
    inference(instantiate,[status(thm)],[s0]) ).

fof(s14,plain,
    ? [X1] : t,
    inference(instantiate,[status(thm)],[s13]) ).

fof(s15,plain,
    t,
    inference(skolemize,[status(esa),new_symbols(skolem,[sK0]),skolemize(X1,sK0)],[s14]) ).

fof(s16,plain,
    ( ! [X2] :
      ? [X1] : t
    & ! [X4] :
      ? [X5] : ~ q(c) ),
    inference(conjunction,[status(thm)],[s13,s2]) ).

fof(s17,plain,
    a = a,
    inference(reflexivity,[status(thm)],[s2]) ).

fof(s18,plain,
    ? [X11] :
      ( ! [X2] :
        ? [X1] : t
      & ! [X4] :
        ? [X5] : ~ q(X11) ),
    inference(existential_gen,[status(thm)],[s16]) ).

fof(s19,plain,
    ! [X2] :
    ? [X1] : t,
    inference(split_conjunct,[status(thm)],[s16]) ).

fof(s20,plain,
    ! [X2] :
    ? [X1] : t,
    inference(instantiate,[status(thm)],[s11]) ).

fof(s21,plain,
    ? [X12] :
      ( q(X12)
      | ~ q(X12) ),
    inference(existential_gen,[status(thm)],[s5]) ).

fof(s22,plain,
    ? [X13,X5] : ~ q(X13),
    inference(existential_gen,[status(thm)],[s7]) ).

fof(s23,plain,
    ! [X4] 