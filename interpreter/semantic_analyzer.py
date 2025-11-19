from lexer import tokenize
from parser import Parser, ParserError
import re

# --------------------------
# Track variable information
# --------------------------
class SymbolTable:
    def __init__(self):
        self.symbols = {}  # { var_name: type }

    def declare(self, name, value_type="NOOB"):
        if name in self.symbols:
            return f"Semantic Error: Variable '{name}' redeclared."
        self.symbols[name] = value_type
        return None

    def get_type(self, name):
        return self.symbols.get(name, None)

    def is_declared(self, name):
        return name in self.symbols
    
    def set_type(self, name, typ):
        if name in self.symbols:
            self.symbols[name] = typ

# -----------------------------
# Infer type from a token value
# -----------------------------
def infer_type(token):
    ttype, val = token[:2]
    if ttype == "INT_LITERAL":
        return "NUMBR"
    elif ttype == "FLOAT_LITERAL":
        return "NUMBAR"
    elif ttype == "STRING":
        return "YARN"
    elif ttype in ("BOOL_TRUE", "BOOL_FALSE"):
        return "TROOF"
    else:
        return "NOOB"  # default / unknown type

# -----------------------------------------------------
# Recursively validate arithmetic or SMOOSH expressions
# -----------------------------------------------------
def validate_expression(tokens, table, line_num, errors):
    if not tokens:
        return "NOOB"

    token = tokens[0]
    ttype, val = token[:2]

    # Literal or identifier
    if ttype in ("INT_LITERAL", "FLOAT_LITERAL", "STRING", "BOOL_TRUE", "BOOL_FALSE"):
        return infer_type(token)
    elif ttype == "IDENTIFIER":
        if not table.is_declared(val):
            errors.append(f"Line {line_num}: Variable '{val}' used before declaration.")
            return "NOOB"
        return table.get_type(val)

    # Arithmetic operations: SUM OF, DIFF OF, PRODUKT OF, QUOSHUNT OF, MOD OF
    if val in ("SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF"):
        # Split operands by AN
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

        if len(operands) < 2:
            errors.append(f"Line {line_num}: Not enough operands for '{val}'.")
            return "NOOB"

        # Validate all operands recursively
        operand_types = [validate_expression(op, table, line_num, errors) for op in operands]

        # NUMBAR takes precedence over NUMBR
        if "YARN" in operand_types:
            errors.append(f"Line {line_num}: Invalid operand type 'YARN' for arithmetic '{val}'.")
            return "NOOB"
        if "NUMBAR" in operand_types:
            return "NUMBAR"
        return "NUMBR"

    # SMOOSH: string concatenation
    if val == "SMOOSH":
        # Split by AN and validate each part
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

        types = [validate_expression(op, table, line_num, errors) for op in operands]
        if any(t != "YARN" for t in types):
            errors.append(f"Line {line_num}: SMOOSH can only concatenate strings.")
        return "YARN"

    # Default fallback
    return "NOOB"

# --------------------------------------------
# Check VISIBLE strings for special characters
# --------------------------------------------
def validate_visible(tokens, table, line_num, errors):
    for tok in tokens:
        ttype, val = tok
        if ttype == "IDENTIFIER":
            if not table.is_declared(val):
                errors.append(f"Line {line_num}: Variable '{val}' used before declaration.")
        elif ttype == "STRING":
            # Example: Allow printable characters including punctuation
            if not re.match(r'^".*"$', val):
                errors.append(f"Line {line_num}: Invalid characters in string {val}.")

# --------------------------------------------
# Perform semantic checks line by line
# --------------------------------------------
def analyze_semantics(filename):
    # Check syntax first
    syntax_errors = validate_file(filename)
    if syntax_errors:
        print("Syntax errors detected — semantic analysis skipped.")
        for err in syntax_errors:
            print("  -", err)
        return

    print("\nNo syntax errors. Proceeding with semantic analysis...\n")

    table = SymbolTable()
    errors = []

    with open(filename, "r") as f:
        for line_num, line in enumerate(f, start=1):
            tokens = tokenize(line)
            if not tokens:
                continue

            first_tok, *rest = tokens
            kind, value = first_tok[:2]

            # Variable declarations: I HAS A var [ITZ value]
            if value == "I HAS A":
                if len(tokens) >= 3:
                    var_name = tokens[2][1]
                    err = table.declare(var_name, "NOOB")
                    if err:
                        errors.append(f"Line {line_num}: {err}")
                    
                    # Check for ITZ initializer
                    if len(tokens) > 3 and tokens[3][1] == "ITZ" and len(tokens) > 4:
                        init_type = validate_expression(tokens[4:], table, line_num, errors)
                        table.set_type(var_name, init_type)
            

            # Variable assignment: var R expr
            elif len(tokens) >= 3 and tokens[1][1] == "R":
                var_name = tokens[0][1]
                if not table.is_declared(var_name):
                    errors.append(f"Line {line_num}: Variable '{var_name}' used before declaration.")
                expr_type = validate_expression(tokens[2:], table, line_num, errors)
                table.set_type(var_name, expr_type)

            # VISIBLE statements
            elif value == "VISIBLE":
                validate_visible(rest, table, line_num, errors)
                
            # Check arithmetic expressions anywhere in line
            elif any(tok[1] in ("SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "SMOOSH") for tok in tokens):
                validate_expression(tokens, table, line_num, errors)
                
    # Display results
    if errors:
        print("Semantic Errors Found:")
        for e in errors:
            print("  -", e)
    else:
        print("No semantic errors found. ✅")

    # Optional: print symbol table for debugging
    print("\nSymbol Table:")
    for name, typ in table.symbols.items():
        print(f"  {name} : {typ}")