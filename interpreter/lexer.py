import re

# Define token types with readable names
token_specs = [
    # COMMENT
    ("COMMENT", r"BTW[^\n]*"),                      # single-line
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
    
    # RESERVED IDENTIFIERS
    ("SMOOSH", r"\bSMOOSH\b"),
    
    # LITERALS
    ("FLOAT_LITERAL", r"-?\d+\.\d+"),       # NUMBAR_LITERAL 
    ("INT_LITERAL", r"-?\d+"),              # NUMBR_LITERAL  
    ("STRING", r'"[^"\n]*"'),               # YARN_LITERAL
    
    ("BOOL_TRUE", r"WIN"),                  # TROOF LITERAL
    ("BOOL_FALSE", r"FAIL"),
           
    # IDENTIFIER:   FUNCIDENT, LOOPIDENT, VARIDENT
    ("IDENTIFIER", r"[A-Za-z][A-Za-z0-9_]*"),
    
    # OTHERS
    ("NEWLINE", r"\n"),
    ("WHITESPACE", r"[ \t\r]+"),
]

# Build regex
token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_specs)

# Tokenizer
def tokenize(code):
    tokens = []
    line_num = 1
    line_start = 0
    
    # Iterate through all matches of defined token patterns in the source code
    for match in re.finditer(token_regex, code):
        kind = match.lastgroup      # Type of token matched
        value = match.group()       # The actual text matched
        start = match.start()
        
        # Ignore comments and spaces
        if kind in ["WHITESPACE", "NEWLINE", "COMMENT", "COMMENT_MULTI"]:
            continue
        
        # Track newlines
        if kind == "NEWLINE":
            line_num += 1
            line_start = match.end()
            continue

        # Store token type and value
        col_num = start - line_start + 1
        tokens.append((kind, value, line_num, col_num))
        
    return tokens