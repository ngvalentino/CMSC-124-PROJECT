import re

# Define token types with readable names
token_specs = [
    # COMMENT
    ("COMMENT", r"BTW*"),                      # single-line
    ("COMMENT_MULTI", r"OBTW[\s\S]*?TLDR"),     # multi-line
    
    # CODE DELIMITER
    ("CODE_DELIMITER", r"HAI|KTHXBYE"),
    
    # VARIABLE LIST DELIMITER
    ("VAR_LIST_DELIMITER", r"WAZZUP|BUHBYE"),
    
    # VARIABLE DECLARATION
    ("VAR_DECLARATION", r"I HAS A"),
    
    # VARIABLE ASSIGNMENT
    ("VAR_ASSIGNMENT", r"ITZ|R"),
    
    # OUTPUT KEYWORD
    ("OUTPUT_KEYWORD", r"VISIBLE|INVISIBLE"),
    
    # ARITHMETIC OPERATORS
    ("ARITHMETIC_OPERATOR", r"SUM OF|DIFF OF|PRODUKT OF|QUOSHUNT OF|MOD OF"),
    
    # COMPARISON OPERATORS
    ("COMPARISON_OPERATOR", r"BIGGR OF|SMALLR OF|BOTH_SAEM|DIFFRINT"),
    
    # LOGICAL OPERATORS
    ("LOGICAL_OPERATOR", r"BOTH OF|EITHER OF|WON OF|NOT|ANY|OF|ALL OF"),
    
    # CONTROL FLOW
    ("CONTROL_FLOW", r"O RLY|YA RLY|MEBBE|NO WAI|OIC|WTF|OMG|OMGWTF|AWSUM THX|O NOES|PLZ|KTHNX|GTFO|FOUND YR"),
    
    # LOOPING
    ("LOOPING", r"IM IN YR|UPPIN|NERFIN|YR|TIL|WILE|IM OUTTA YR"),
    
    # FUNCTION DEFINITION AND CALL
    ("FUNCTION_DEF_CALL", r"HOW IZ I|IF U SAY SO|I IZ|MKAY"),
    
    # MULTIPLE PARAM SEPARATOR
    ("MULTI_PARAM_SEPARATOR", r"AN"),
    
    # INPUT AND OUTPUT
    ("IO", r"GIMMEH"),
    
    # TYPE AND CASTING
    ("MAEK", r"\bMAEK\b"),
    ("A", r"\bA\b"),
    ("IS_NOW_A", r"\bIS NOW A\b"),
    ("TYPE_LITERAL", r"\b(?:NUMBR|NUMBAR|YARN|TROOF|NOOB)\b"),
    
    # LITERALS
    ("FLOAT_LITERAL", r"-?\d+\.\d+"),       # NUMBAR_LITERAL 
    ("INT_LITERAL", r"-?\d+"),              # NUMBR_LITERAL  
    ("STRING", r'"[^"\n]*"'),               # YARN_LITERAL
    
    ("BOOL_TRUE", r"WIN"),                  # TROOF LITERAL
    ("BOOL_FALSE", r"FAIL"),
           
    # IDENTIFIER:   FUNCIDENT, LOOPIDENT, VARIDENT
    ("IDENTIFIER", r"[A-Za-z][A-Za-z0-9_]\w*"),
    
    # OTHERS
    ("NEWLINE", r"\n"),
    ("WHITESPACE", r"[ \t\r]+"),
    ("SMOOSH", r"\bSMOOSH\b"),
]

# Build regex
token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_specs)
get_token = re.compile(token_regex).finditer

# Format for printing
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
}

# Tokenizer
def tokenize(code):
    tokens = []
    
    # Iterate through all matches of defined token patterns in the source code
    for match in re.finditer(token_regex, code):
        kind = match.lastgroup      # Type of token matched
        value = match.group()       # The actual text matched
        
        # Ignore comments and spaces
        if kind in ["WHITESPACE", "NEWLINE", "COMMENT", "COMMENT_MULTI"]:
            continue
        
        # Store token type and value
        tokens.append((kind, value))
    return tokens

# Main
def main():
    # Read LOLCODE source
    with open("test.lol", "r") as file:
        code = file.read()

    # Tokenize the input source code
    tokens = tokenize(code)

    # Write formatted tokens to the output file
    with open("output.txt", "w") as out:
        for kind, value in tokens:
            
            # Retrieve format label for the token type
            label = token_labels.get(kind)
            
            if label:
                # Handle string literals separately to show delimiters
                if kind in ["STRING"]:
                    out.write(f'String Delimiter " \n')
                    inner_value = value.strip('"')          # remove quotes
                    out.write(f'{label} {inner_value} {inner_value}\n')
                    out.write(f'String Delimiter " \n')
                
                # Handle numeric and boolean literals
                elif kind in ["INT_LITERAL", "FLOAT_LITERAL", "BOOL_TRUE", "BOOL_FALSE"]:
                    out.write(f"{label} {value} {value}\n")
                
                # Handle all other token types normally
                else:
                    out.write(f"{label} {value}\n")

    print("Tokenization complete!! See output.txt")
    
if __name__ == "__main__":
    main()
