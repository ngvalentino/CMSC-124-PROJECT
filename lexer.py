import re

token_specs = [
    ("COMMENT", r"BTW.*"),
    ("COMMENT_MULTI", r"OBTW[\s\S]*?TLDR"),
    ("CODE_DELIMITER", r"HAI|KTHXBYE"),
    ("VAR_LIST_DELIMITER", r"WAZZUP|BUHBYE"),
    ("VAR_DECLARATION", r"I HAS A"),
    ("VAR_ASSIGNMENT", r"ITZ|R"),
    ("OUTPUT_KEYWORD", r"VISIBLE|INVISIBLE"),
    ("ARITHMETIC_OPERATOR", r"SUM OF|DIFF OF|PRODUKT OF|QUOSHUNT OF|MOD OF"),
    ("COMPARISON_OPERATOR", r"BOTH SAEM|DIFFRINT"),
    ("LOGICAL_OPERATOR", r"BOTH OF|EITHER OF|WON OF|NOT|ANY|OF|ALL OF"),
    ("CONTROL_FLOW", r"O RLY|YA RLY|MEBBE|NO WAI|OIC|WTF|OMG|OMGWTF|AWSUM THX|O NOES|PLZ|KTHNX|GTFO|FOUND YR"),
    ("YR", r"\bYR\b"),
    ("LOOPING", r"IM IN YR|UPPIN|NERFIN|TIL|WILE|IM OUTTA YR"),
    ("FUNCTION_DEF_CALL", r"HOW IZ I|IF U SAY SO"),
    ("FUNCTION_CALL", r"I IZ"),
    ("FUNCTION_END", r"\bMKAY\b"),
    ("MULTI_PARAM_SEPARATOR", r"AN"),
    ("IO", r"GIMMEH"),
    ("MAEK", r"\bMAEK\b"),
    ("A", r"\bA\b"),
    ("IS_NOW_A", r"\bIS NOW A\b"),
    ("TYPE_LITERAL", r"\b(?:NUMBR|NUMBAR|YARN|TROOF|NOOB)\b"),
    ("FLOAT_LITERAL", r"-?\d+\.\d+"),
    ("INT_LITERAL", r"-?\d+"),
    ("STRING", r'"[^"\n]*"'),
    ("BOOL_TRUE", r"WIN"),
    ("BOOL_FALSE", r"FAIL"),
    ("IDENTIFIER", r"\b[A-Za-z][A-Za-z0-9_]*\b"),
    ("NEWLINE", r"\n"),
    ("WHITESPACE", r"[ \t\r]+"),
    ("SMOOSH", r"\bSMOOSH\b"),
]

token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_specs)

def tokenize(code):
    tokens = []
    for match in re.finditer(token_regex, code):
        kind = match.lastgroup
        value = match.group()
        if kind in ["WHITESPACE", "NEWLINE", "COMMENT", "COMMENT_MULTI"]:
            continue
        tokens.append((kind, value))
    return tokens