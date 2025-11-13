from lexer import tokenize

#expression token types
expression_tokens = {
    "INT_LITERAL", "FLOAT_LITERAL", "STRING", "IDENTIFIER", "BOOL_TRUE", "BOOL_FALSE"
}

#grammar rules
grammar_rules = {
    "VAR_DECLARATION": [
        ["VAR_DECLARATION", "IDENTIFIER"],
        ["VAR_DECLARATION", "IDENTIFIER", "VAR_ASSIGNMENT", "EXPR"]
    ],
    "OUTPUT_KEYWORD": [["OUTPUT_KEYWORD", "EXPR"]],
    "IO": [["IO", "IDENTIFIER"]],
    "VAR_ASSIGNMENT": [["IDENTIFIER", "VAR_ASSIGNMENT", "EXPR"]],
    "ARITHMETIC_OPERATOR": [["ARITHMETIC_OPERATOR", "EXPR", "MULTI_PARAM_SEPARATOR", "EXPR"]],
    "SMOOSH": [["SMOOSH", "EXPR", "MULTI_PARAM_SEPARATOR", "EXPR"]],
    "TYPECAST": [["MAEK", "EXPR", "A", "TYPE_LITERAL"]],
    "COMPARISON_OPERATOR": [["COMPARISON_OPERATOR", "EXPR", "EXPR"]],
    "FUNCTION_CALL": [["FUNCTION_CALL", "IDENTIFIER", "YR", "EXPR", "FUNCTION_END"]],
    "RETURN": [["CONTROL_FLOW", "EXPR"]],  #FOUND YR
    "EXIT": [["CONTROL_FLOW"]],            #GTFO

    #for block-based constructs
    "CONTROL_FLOW": {
        "O RLY": "start_conditional",
        "YA RLY": "inside_conditional",
        "NO WAI": "inside_conditional",
        "OIC": "end_conditional"
    },
    "FUNCTION_DEF_CALL": {
        "HOW IZ I": "start_function",
        "IF U SAY SO": "end_function"
    },
    "LOOPING": {
        "IM IN YR": "start_loop",
        "IM OUTTA YR": "end_loop"
    },
    "EXCEPTION": {
        "PLZ": "start_try",
        "AWSUM THX": "try_block",
        "O NOES": "catch_block"
    },
    "SWITCH": {
        "OMG": "start_case",
        "OMGWTF": "default_case",
        "OIC": "end_case"
    }
}

#parser state for block tracking
class ParserState:
    def __init__(self):
        self.stack = []
    #pushes a new block onto the stack
    def enter_block(self, block_type):
        self.stack.append(block_type)

    #checks if the top of the stack matches the expected block type
    def exit_block(self, block_type):
        if not self.stack or self.stack[-1] != block_type:
            return False
        self.stack.pop()
        return True
    
    #returns the most recently opened block (top of the stack), or None if the stack is empty
    def current_block(self):
        return self.stack[-1] if self.stack else None

    #checks whether a specific block type is currently open
    def is_inside(self, block_type):
        return block_type in self.stack

    #returns True if there are any blocks left open
    def has_unclosed_blocks(self):
        return bool(self.stack)

    #returns a list of all currently open blocks
    def get_unclosed_blocks(self):
        return list(self.stack)

#check if token type is an expression
def is_expr(token_type):
    return token_type in expression_tokens

#match token sequence to a grammar pattern
def match_pattern(tokens, pattern):
    if len(tokens) < len(pattern):
        return False
    for i, expected in enumerate(pattern):
        actual = tokens[i][0]
        if expected == "EXPR":
            if not is_expr(actual):
                return False
        elif expected != actual:
            return False
    return True

#check syntax of a single line
def check_line_syntax(tokens, state, line_num):
    if not tokens:
        #blank lines are valid
        return True, None

    kind, value = tokens[0]

    #single-line rules
    #checks if the first token type matches a grammar rule key
    if kind in grammar_rules and isinstance(grammar_rules[kind], list):
        for pattern in grammar_rules[kind]:
            if match_pattern(tokens, pattern):
                return True, None
        return False, f"Line {line_num}: Invalid syntax → {' '.join(tok[1] for tok in tokens)}"
    
    #if not, checks all grammar rules
    #full-line patterns
    for rule_key, patterns in grammar_rules.items():
        if isinstance(patterns, list):
            for pattern in patterns:
                if match_pattern(tokens, pattern):
                    return True, None

    #handle the validation logic for blocks statements
    #block-based rules
    if kind in grammar_rules and isinstance(grammar_rules[kind], dict):
        action = grammar_rules[kind].get(value)
        if action == "start_conditional":
            state.enter_block("O RLY")
        elif action == "end_conditional":
            if not state.exit_block("O RLY"):
                return False, f"Line {line_num}: Unexpected OIC without O RLY"
        elif action == "start_function":
            state.enter_block("HOW IZ I")
        elif action == "end_function":
            if not state.exit_block("HOW IZ I"):
                return False, f"Line {line_num}: Unexpected IF U SAY SO without HOW IZ I"
        elif action == "start_loop":
            state.enter_block("IM IN YR")
        elif action == "end_loop":
            if not state.exit_block("IM IN YR"):
                return False, f"Line {line_num}: Unexpected IM OUTTA YR without IM IN YR"
        elif action == "start_try":
            state.enter_block("PLZ")
        elif action == "catch_block":
            if not state.is_inside("PLZ"):
                return False, f"Line {line_num}: O NOES without PLZ"
        elif action == "start_case":
            state.enter_block("OMG")
        elif action == "end_case":
            if not state.exit_block("OMG"):
                return False, f"Line {line_num}: OIC without OMG"
        return True, None

    return True, None

#validate a full file
def validate_file(filename):
    errors = []
    state = ParserState()
    with open(filename, "r") as f:
        for line_num, line in enumerate(f, start=1):
            tokens = tokenize(line)
            print(f"Line {line_num} tokens: {tokens}") 
            valid, error = check_line_syntax(tokens, state, line_num)
            if not valid and error:
                errors.append(error)

    if state.has_unclosed_blocks():
        for block in state.get_unclosed_blocks():
            errors.append(f"Unclosed block: {block}")

    return errors

#run the validator
if __name__ == "__main__":
    file = "test2.lol"
    errors = validate_file(file)
    if errors:
        print("Syntax Errors Found:")
        for err in errors:
            print(err)
    else:
        print("All lines are syntactically correct!")