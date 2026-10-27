"""
Propositional Logic Parser
---------------------------
Parses a propositional logic expression written with variables (single
uppercase letters, e.g. P, Q, R) and the operators:

    NOT   : ¬  or  !  or  ~
    AND   : ∧  or  &  or  ^^  (avoid ^ alone -> XOR not required by spec)
    OR    : ∨  or  |
    IMPLY : →  or  ->
    IFF   : ↔  or  <->

Produces an Abstract Syntax Tree (AST) of Node objects which can then be
deterministically evaluated for every truth assignment (truth_table.py) or
walked for symbolic transforms (evaluator.py, contrapositive.py).

This parser is intentionally small and dependency free (no external
libraries) so the "mathematical correctness" of the system depends only on
code we can read end-to-end, not on any AI model's judgement.
"""

import re

# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

TOKEN_SPEC = [
    ("IFF",     r"<->|↔"),
    ("IMPLY",   r"->|→"),
    ("AND",     r"&&|&|∧"),
    ("OR",      r"\|\||\||∨"),
    ("NOT",     r"!|~|¬"),
    ("LPAREN",  r"\("),
    ("RPAREN",  r"\)"),
    ("VAR",     r"[A-Za-z][A-Za-z0-9]*"),
    ("SKIP",    r"[ \t]+"),
]

MASTER_RE = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))


class LogicSyntaxError(Exception):
    pass


def tokenize(expr):
    tokens = []
    pos = 0
    while pos < len(expr):
        m = MASTER_RE.match(expr, pos)
        if not m:
            raise LogicSyntaxError(f"Unrecognized symbol at position {pos}: '{expr[pos]}'")
        kind = m.lastgroup
        text = m.group()
        if kind != "SKIP":
            tokens.append((kind, text))
        pos = m.end()
    return tokens


# ---------------------------------------------------------------------------
# AST Nodes
# ---------------------------------------------------------------------------

class Node:
    kind = None

    def variables(self):
        raise NotImplementedError

    def to_string(self):
        raise NotImplementedError

    def evaluate(self, env):
        raise NotImplementedError


class VarNode(Node):
    kind = "VAR"

    def __init__(self, name):
        self.name = name

    def variables(self):
        return {self.name}

    def to_string(self):
        return self.name

    def evaluate(self, env):
        if self.name not in env:
            raise LogicSyntaxError(f"No truth value provided for variable '{self.name}'")
        return env[self.name]


class NotNode(Node):
    kind = "NOT"

    def __init__(self, child):
        self.child = child

    def variables(self):
        return self.child.variables()

    def to_string(self):
        inner = self.child.to_string()
        if self.child.kind not in ("VAR", "NOT"):
            inner = f"({inner})"
        return f"¬{inner}"

    def evaluate(self, env):
        return not self.child.evaluate(env)


class BinaryNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def variables(self):
        return self.left.variables() | self.right.variables()

    def _op_symbol(self):
        raise NotImplementedError

    def to_string(self):
        l = self.left.to_string()
        r = self.right.to_string()
        if self.left.kind not in ("VAR", "NOT"):
            l = f"({l})"
        if self.right.kind not in ("VAR", "NOT"):
            r = f"({r})"
        return f"{l} {self._op_symbol()} {r}"


class AndNode(BinaryNode):
    kind = "AND"

    def _op_symbol(self):
        return "∧"

    def evaluate(self, env):
        return self.left.evaluate(env) and self.right.evaluate(env)


class OrNode(BinaryNode):
    kind = "OR"

    def _op_symbol(self):
        return "∨"

    def evaluate(self, env):
        return self.left.evaluate(env) or self.right.evaluate(env)


class ImplyNode(BinaryNode):
    kind = "IMPLY"

    def _op_symbol(self):
        return "→"

    def evaluate(self, env):
        return (not self.left.evaluate(env)) or self.right.evaluate(env)


class IffNode(BinaryNode):
    kind = "IFF"

    def _op_symbol(self):
        return "↔"

    def evaluate(self, env):
        return self.left.evaluate(env) == self.right.evaluate(env)


# ---------------------------------------------------------------------------
# Recursive-descent parser
# Grammar (lowest to highest precedence):
#   iff    -> implication ( '<->' implication )*
#   implication -> or ( '->' or )*        (right-assoc handled as chain; fine for 2-op typical use)
#   or     -> and ( '|' and )*
#   and    -> not ( '&' not )*
#   not    -> '!' not | atom
#   atom   -> VAR | '(' iff ')'
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def advance(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def expect(self, kind):
        tok = self.peek()
        if tok[0] != kind:
            raise LogicSyntaxError(f"Expected {kind} but found {tok}")
        return self.advance()

    def parse(self):
        node = self.parse_iff()
        if self.pos != len(self.tokens):
            raise LogicSyntaxError(f"Unexpected token at end: {self.peek()}")
        return node

    def parse_iff(self):
        node = self.parse_implication()
        while self.peek()[0] == "IFF":
            self.advance()
            rhs = self.parse_implication()
            node = IffNode(node, rhs)
        return node

    def parse_implication(self):
        node = self.parse_or()
        # right-associative chain: P -> Q -> R  means P -> (Q -> R)
        if self.peek()[0] == "IMPLY":
            self.advance()
            rhs = self.parse_implication()
            node = ImplyNode(node, rhs)
        return node

    def parse_or(self):
        node = self.parse_and()
        while self.peek()[0] == "OR":
            self.advance()
            rhs = self.parse_and()
            node = OrNode(node, rhs)
        return node

    def parse_and(self):
        node = self.parse_not()
        while self.peek()[0] == "AND":
            self.advance()
            rhs = self.parse_not()
            node = AndNode(node, rhs)
        return node

    def parse_not(self):
        if self.peek()[0] == "NOT":
            self.advance()
            child = self.parse_not()
            return NotNode(child)
        return self.parse_atom()

    def parse_atom(self):
        kind, text = self.peek()
        if kind == "VAR":
            self.advance()
            return VarNode(text)
        if kind == "LPAREN":
            self.advance()
            node = self.parse_iff()
            self.expect("RPAREN")
            return node
        raise LogicSyntaxError(f"Unexpected token: {(kind, text)}")


def parse_expression(expr: str) -> Node:
    """Parse a propositional logic string into an AST. Raises LogicSyntaxError
    on malformed input -- callers MUST catch this and surface a clean error
    rather than guessing at intent."""
    if not expr or not expr.strip():
        raise LogicSyntaxError("Empty expression")
    tokens = tokenize(expr)
    if not tokens:
        raise LogicSyntaxError("Empty expression")
    parser = Parser(tokens)
    return parser.parse()


def ordered_variables(node: Node):
    """Return variables in first-appearance order (nicer for truth tables
    than an unordered set)."""
    seen = []
    seen_set = set()

    def walk(n):
        if isinstance(n, VarNode):
            if n.name not in seen_set:
                seen_set.add(n.name)
                seen.append(n.name)
        elif isinstance(n, NotNode):
            walk(n.child)
        elif isinstance(n, BinaryNode):
            walk(n.left)
            walk(n.right)

    walk(node)
    return seen
