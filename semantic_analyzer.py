from lexer import tokenize
from parser import validate_file

# Track variable information
class SymbolTable:
    def __init__(self):
        self.symbols = {}  # { var_name: type }

    def declare(self, name, value_type):
        if name in self.symbols:
            return f"Semantic Error: Variable '{name}' redeclared."
        self.symbols[name] = value_type
        return None

    def get_type(self, name):
        return self.symbols.get(name, None)

    def is_declared(self, name):
        return name in self.symbols


# Infer type from a token value
def infer_type(token):
    ttype, val = token
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


# Perform semantic checks line by line
def analyze_semantics(filename):
    # Step 1: check syntax first
    syntax_errors = validate_file(filename)
    if syntax_errors:
        print("Syntax errors detected — semantic analysis skipped.")
        for err in syntax_errors:
            print(err)
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
            kind, value = first_tok

            # Variable declarations: I HAS A var [ITZ value]
            if value == "I HAS A":
                if len(tokens) >= 3:
                    var_name = tokens[2][1]
                    err = table.declare(var_name, "NOOB")
                    if err:
                        errors.append(f"Line {line_num}: {err}")
                    # Check for ITZ initializer
                    if len(tokens) > 3 and tokens[3][1] == "ITZ":
                        if len(tokens) > 4:
                            init_type = infer_type(tokens[4])
                            table.symbols[var_name] = init_type
                elif len(tokens) == 2:
                    var_name = tokens[1][1]
                    err = table.declare(var_name, "NOOB")
                    if err:
                        errors.append(f"Line {line_num}: {err}")

            # Variable assignment: var R expr
            elif len(tokens) >= 3 and tokens[1][1] == "R":
                var_name = tokens[0][1]
                if not table.is_declared(var_name):
                    errors.append(f"Line {line_num}: Variable '{var_name}' used before declaration.")
                # Type inference for the expression
                expr_type = infer_type(tokens[2])
                if table.is_declared(var_name):
                    table.symbols[var_name] = expr_type

            # Arithmetic operations (SUM OF, DIFF OF, etc.)
            elif any(tok[1] in ("SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF") for tok in tokens):
                num_tokens = [tok for tok in tokens if tok[0] in ("INT_LITERAL", "FLOAT_LITERAL", "IDENTIFIER")]
                for tok in num_tokens:
                    if tok[0] == "IDENTIFIER" and not table.is_declared(tok[1]):
                        errors.append(f"Line {line_num}: Variable '{tok[1]}' used before declaration.")
                    elif tok[0] == "STRING":
                        errors.append(f"Line {line_num}: Invalid operand type (string) for arithmetic.")

            # VISIBLE statements
            elif value == "VISIBLE":
                for tok in rest:
                    if tok[0] == "IDENTIFIER" and not table.is_declared(tok[1]):
                        errors.append(f"Line {line_num}: Variable '{tok[1]}' used before declaration.")

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


# Run semantic analyzer directly
if __name__ == "__main__":
    test_file = "test2.lol"
    analyze_semantics(test_file)
