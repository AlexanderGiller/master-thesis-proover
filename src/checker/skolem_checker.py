from lark import Tree


class SkolemError(Exception):
    pass


def get_universal_vars_in_scope(formula_tree, existential_var: str) -> set[str]:
    """
    Walk the formula tree to find which universally quantified
    variables are in scope at the point where `existential_var`
    is bound by an existential quantifier.
    """

    # Traverse quantifiers depth-first, tracking scope
    def walk(node, universal_scope):
        if not isinstance(node, Tree):
            return None
        if node.data == "fof_quantified_formula":
            quantifier = node.children[0].data  # "forall" or "exists"
            variables = [str(v) for v in node.children[1].children]
            body = node.children[2]
            if quantifier == "exists" and existential_var in variables:
                return set(universal_scope)  # found it — return scope
            new_scope = (
                universal_scope | set(variables) if quantifier == "forall" else universal_scope
            )
            return walk(body, new_scope)
        for child in node.children:
            result = walk(child, universal_scope)
            if result is not None:
                return result
        return None

    return walk(formula_tree, set()) or set()


def check_skolemization(step, parent_step):
    inf = step.inference

    if inf.rule != "skolemize":
        raise SkolemError(f"[{step.name}] Expected rule 'skolemize', got '{inf.rule}'")

    if inf.status != "esa":
        raise SkolemError(f"[{step.name}] Skolemization must have status 'esa'")

    # Fix: explicitly check for None OR wrong length
    if inf.new_symbols is None or len(inf.new_symbols) != 1:
        raise SkolemError(f"[{step.name}] Must introduce exactly one Skolem symbol")

    if inf.skolem_var is None or inf.skolem_term is None:
        raise SkolemError(f"[{step.name}] Missing skolemize(Var, sk(...)) annotation")

    # scope check only if parent has a real formula tree
    if parent_step.formula is not None:
        expected_scope = get_universal_vars_in_scope(
            parent_step.formula, inf.skolem_var
        )
        skolem_args = extract_skolem_term_args(inf.skolem_term)
        if set(skolem_args) != expected_scope:
            raise SkolemError(
                f"[{step.name}] Skolem term args {skolem_args} don't match "
                f"expected scope {expected_scope}"
            )


def extract_skolem_term_args(term_tree) -> list[str]:
    """Pull out argument variable names from a Skolem term node."""
    if isinstance(term_tree, Tree) and term_tree.data == "compound_term":
        args_node = term_tree.children[1]  # fof_arguments
        return [str(a.children[0]) for a in args_node.children]
    return []
