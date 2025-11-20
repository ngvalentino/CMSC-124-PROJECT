from lexer import tokenize, filter_tokens
from tree_parser import TreeParser, ParserError


# ==========================================================
# Symbol Table
# ==========================================================
class SymbolTable:
    def __init__(self):
        self.symbols = {}  # { var_name: value }

    def declare(self, name, value=None):
        if name in self.symbols:
            return f"Semantic Error: Variable '{name}' redeclared."
        self.symbols[name] = value
        return None

    def is_declared(self, name):
        return name in self.symbols

    def set_value(self, name, value):
        if name in self.symbols:
            self.symbols[name] = value

    def get_value(self, name):
        return self.symbols.get(name)


# ==========================================================
# Expression Evaluator for AST Nodes
# ==========================================================
def eval_ast(node, table: SymbolTable, errors: list):
    # ---------- Literals ----------
    if node.node_type == "LITERAL":
        val = node.value
        if val.isdigit():
            return int(val)
        try:
            return float(val)
        except ValueError:
            return val  # string literal

    # ---------- Identifier ----------
    if node.node_type == "IDENTIFIER":
        name = node.value
        if not table.is_declared(name):
            errors.append(f"Variable '{name}' used before declaration.")
            return None
        return table.get_value(name)

    # ---------- Operations (SUM OF, DIFF OF, etc.) ----------
    if node.node_type == "OP":
        op = node.value
        operands = [eval_ast(child, table, errors) for child in node.children]

        if any(v is None for v in operands):
            return None

        if op == "SUM OF":
            return sum(operands)

        elif op == "DIFF OF":
            res = operands[0]
            for n in operands[1:]:
                res -= n
            return res

        elif op == "PRODUKT OF":
            res = operands[0]
            for n in operands[1:]:
                res *= n
            return res

        elif op == "QUOSHUNT OF":
            res = operands[0]
            for n in operands[1:]:
                res /= n
            return res

        elif op == "MOD OF":
            res = operands[0]
            for n in operands[1:]:
                res %= n
            return res

    # ---------- SMOOSH ----------
    if node.node_type == "SMOOSH":
        parts = [str(eval_ast(child, table, errors)) for child in node.children]
        return "".join(parts)

    return None


# ==========================================================
# AST Walker for Semantic Analysis
# ==========================================================
def walk_ast(node, table: SymbolTable, errors: list):
    # ---------- Variable Declaration ----------
    if node.node_type == "VAR_DEC":
        var_name = node.children[0].value
        err = table.declare(var_name)
        if err:
            errors.append(err)

        if len(node.children) > 1:
            init_value = eval_ast(node.children[1], table, errors)
            table.set_value(var_name, init_value)

    # ---------- Assignment ----------
    elif node.node_type == "ASSIGN":
        var_name = node.children[0].value
        if not table.is_declared(var_name):
            errors.append(f"Variable '{var_name}' used before declaration.")
        else:
            value = eval_ast(node.children[1], table, errors)
            table.set_value(var_name, value)

    # ---------- VISIBLE ----------
    elif node.node_type == "PRINT":
        for expr in node.children:
            eval_ast(expr, table, errors)  # detect undeclared usage

    # ---------- Other constructs ----------
    # BLOCK, IF, LOOP, etc.
    for child in node.children:
        walk_ast(child, table, errors)


# ==========================================================
# Main Entry Point
# ==========================================================
def analyze_semantics_from_code(code):
    # ---------- Syntax Check ----------
    try:
        tokens = tokenize(code)
        clean_tokens = filter_tokens(tokens)
        parser = TreeParser(clean_tokens)
        ast_root = parser.parse_program()
    except ParserError as e:
        return [str(e)], {}

    # ---------- Semantic Check ----------
    table = SymbolTable()
    errors = []

    walk_ast(ast_root, table, errors)

    return errors, table.symbols
