from lexer import tokenize, filter_tokens
from parser import Parser, ParserError

# --------------------------
# Track variable information
# --------------------------
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

# -----------------------------
# Recursive expression evaluation
# -----------------------------
def evaluate_expression(tokens, table, line_num, errors):
    if not tokens:
        return None

    ttype, val = tokens[0][:2]

    # -----------------
    # Literal
    # -----------------
    if ttype in ("INT_LITERAL", "FLOAT_LITERAL", "STRING", "BOOL_TRUE", "BOOL_FALSE"):
        if ttype == "INT_LITERAL":
            return int(val)
        elif ttype == "FLOAT_LITERAL":
            return float(val)
        elif ttype in ("BOOL_TRUE", "BOOL_FALSE"):
            return True if ttype == "BOOL_TRUE" else False
        else:
            return val

    # -----------------
    # Identifier
    # -----------------
    elif ttype == "IDENTIFIER":
        if not table.is_declared(val):
            errors.append(f"Line {line_num}: Variable '{val}' used before declaration.")
            return None
        return table.get_value(val)

    # -----------------
    # Arithmetic operations
    # -----------------
    elif val in ("SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF"):
        operands = []
        current = []
        # split tokens by AN
        for tok in tokens[1:]:
            if tok[1] == "AN":
                if current:
                    operands.append(current)
                    current = []
            else:
                current.append(tok)
        if current:
            operands.append(current)

        if len(operands) < 2:
            errors.append(f"Line {line_num}: Not enough operands for '{val}'.")
            return None

        # recursively evaluate operands
        evals = [evaluate_expression(op, table, line_num, errors) for op in operands]

        # check for None
        if any(e is None for e in evals):
            return None

        # perform operation
        if val == "SUM OF":
            return sum(evals)
        elif val == "DIFF OF":
            res = evals[0]
            for e in evals[1:]:
                res -= e
            return res
        elif val == "PRODUKT OF":
            res = evals[0]
            for e in evals[1:]:
                res *= e
            return res
        elif val == "QUOSHUNT OF":
            res = evals[0]
            for e in evals[1:]:
                res /= e
            return res
        elif val == "MOD OF":
            res = evals[0]
            for e in evals[1:]:
                res %= e
            return res

    # -----------------
    # SMOOSH (string concatenation)
    # -----------------
    elif val == "SMOOSH":
        operands = []
        current = []
        for tok in tokens[1:]:
            if tok[1] == "AN":
                if current:
                    operands.append(current)
                    current = []
            else:
                current.append(tok)
        if current:
            operands.append(current)
        evals = [str(evaluate_expression(op, table, line_num, errors)) for op in operands]
        return ''.join(evals)

    # -----------------
    # Default
    # -----------------
    return None

# -----------------------------
# Semantic Analysis
# -----------------------------
def analyze_semantics(code):
    # -----------------------------
    # Syntax checking
    # -----------------------------
    try:
        all_tokens = tokenize(code)       # Keep all tokens for Treeview if needed
        parser_tokens = filter_tokens(all_tokens)  # Remove comment tokens
        parser = Parser(parser_tokens)
        parser.parse_program()
    except ParserError as e:
        return [str(e)], {}

    # -----------------------------
    # Semantic analysis
    # -----------------------------
    table = SymbolTable()
    errors = []

    for line_num, line in enumerate(code.splitlines(), start=1):
        tokens = filter_tokens(tokenize(line))  # Remove comments per line
        if not tokens:
            continue

        first_tok, *rest = tokens
        kind, value = first_tok[:2]

        # Variable declaration
        if value == "I HAS A":
            # The next token should be the variable name
            if len(tokens) >= 2:
                var_name_tok = tokens[1]
                var_name = var_name_tok[1]
                err = table.declare(var_name)
                if err:
                    errors.append(f"Line {line_num}: {err}")

                # Optional assignment
                if len(tokens) >= 4 and tokens[2][1] == "ITZ":
                    val = evaluate_expression(tokens[3:], table, line_num, errors)
                    table.set_value(var_name, val)


        # Assignment
        elif len(tokens) >= 3 and tokens[1][1] == "R":
            var_name = tokens[0][1]
            if not table.is_declared(var_name):
                errors.append(f"Line {line_num}: Variable '{var_name}' used before declaration.")
            else:
                val = evaluate_expression(tokens[2:], table, line_num, errors)
                table.set_value(var_name, val)

        # VISIBLE
        elif value == "VISIBLE":
            for tok in rest:
                if tok[0] == "IDENTIFIER" and not table.is_declared(tok[1]):
                    errors.append(f"Line {line_num}: Variable '{tok[1]}' used before declaration.")

    return errors, table.symbols

