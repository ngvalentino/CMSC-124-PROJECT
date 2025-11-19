from lexer import tokenize
from parser import Parser, ParserError
from semantic_analyzer import analyze_semantics

token_labels = {
    "CODE_DELIMITER": "Code Delimiter",
    "VAR_LIST_DELIMITER": "Variable List Delimiter",
    "VAR_DECLARATION": "Variable Declaration",
    "VAR_ASSIGNMENT": "Variable Assignment (following I HAS A)",
    "IDENTIFIER": "Variable Identifier",
    "INT_LITERAL": "Integer Literal",
    "FLOAT_LITERAL": "Float Literal",
    "STRING": "String Literal",
    "OUTPUT_KEYWORD": "Output Keyword",
    "ARITHMETIC_OPERATOR": "Arithmetic Operator",
    "COMPARISON_OPERATOR": "Comparison Operator",
    "MULTI_PARAM_SEPARATOR": "Multiple Parameter Separator",
    "BOOL_TRUE": "Boolean Value (True)",
    "BOOL_FALSE": "Boolean Value (False)",
    "SMOOSH": "SMOOSH",
}

def print_tokens(tokens):
    for kind, value, line, col in tokens:
        label = token_labels.get(kind, kind)
        if kind == "STRING":
            inner = value.strip('"')
            print(f'String Delimiter "')
            print(f"{label} {inner} {inner}")
            print(f'String Delimiter "')
        elif kind in ["INT_LITERAL", "FLOAT_LITERAL", "BOOL_TRUE", "BOOL_FALSE"]:
            print(f"{label} {value} {value}")
        else:
            print(f"{label} {value}")

def main():
    filename = "../lol_files/01_variables.lol"

    # === READ FILE ===
    with open(filename, "r") as f:
        code = f.read()
    tokens = tokenize(code)

    # === LEXICAL ANALYSIS ===
    print("=== LEXICAL ANALYSIS ===")
    print_tokens(tokens)
    
    # === SYNTAX ANALYSIS ===
    print("\n=== SYNTAX ANALYSIS ===")
    try:
        parser = Parser(tokens)
        parser.parse_program()  # This will raise ParserError if invalid
        print("No syntax errors found. ✅")
    except ParserError as e:
        print("Syntax error:", e)
        print("\nSemantic analysis skipped due to syntax errors.")
        return

    # === SEMANTIC ANALYSIS ===
    print("\n=== SEMANTIC ANALYSIS ===")
    analyze_semantics(filename)

if __name__ == "__main__":
    main()