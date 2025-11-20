'''
This used the intended implementation for a recursive-descent parser for LOLCODE
'''

from lexer import tokenize

# -------------------------
# Parser Error
# -------------------------
class ParserError(Exception):
    pass

# -------------------------
# Parser Class
# -------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []  # Collect parsing errors
    
    # -------------------------
    # Helpers
    # -------------------------
    def current(self):
        # Skip comments automatically
        while self.pos < len(self.tokens) and self.tokens[self.pos][0].startswith("COMMENT"):
            self.pos += 1
        if self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            return t[0], t[1], t[2], t[3]  
        return None, None, None, None
    
    def advance(self):
        self.pos += 1
    
    def match(self, ttype, value=None):
        token_type, token_value, *_ = self.current()
        if token_type is None:
            return False
        if token_type == ttype and (value is None or token_value == value):
            self.advance()
            return True
        return False
    
    def expect(self, ttype, value=None):
        token_type, token_value, line, col = self.current()  # include line info
        if token_type != ttype or (value is not None and token_value != value):
            # Record error with line info
            self.errors.append(
                f"[Line {line}] Expected {ttype} {value}, got {token_type} {token_value}"
            )
            # Attempt simple recovery: skip until a safe token
            self.advance()
            return {"type": token_type, "value": token_value, "line": line, "col": col}
        
        self.advance()
        return {"type": token_type, "value": token_value, "line": line, "col": col}


    # -------------------------
    # Program Entry
    # -------------------------
    def parse_program(self):
        self.expect("CODE_DELIMITER", "HAI")          # program start
        self.parse_statement_list()
        self.expect("CODE_DELIMITER", "KTHXBYE")      # program end
    
    # -------------------------
    # Statement Parsing
    # -------------------------
    def parse_statement_list(self):
        while True:
            token_type, *_ = self.current()
            if token_type in (None, "CODE_DELIMITER", "OIC", "IF U SAY SO", "IM OUTTA YR", "O NOES"):
                break
            elif token_type == "VAR_LIST_DELIMITER":  # Skip WAZZUP/BUHBYE
                self.advance()
                continue  # skip parsing a statement
            self.parse_statement()

    
    def parse_statement(self):
        token_type, token_value, line, col = self.current()
        try:
            # <print>
            if token_type == "OUTPUT_KEYWORD":
                self.parse_print()
            
            # <declaration>
            elif token_type == "VAR_DECLARATION":
                self.parse_declaration()
                
            # <identifier>
            elif token_type == "IDENTIFIER":
                self.parse_assignment()

            # <conditional>
            elif token_type == "CONTROL_FLOW" and token_value == "O RLY?":
                self.parse_conditional()
                
            # <loop>
            elif token_type == "LOOPING" and token_value == "IM IN YR":
                self.parse_loop()
                
            # <function_def>
            elif token_type == "FUNCTION_DEF_CALL" and token_value == "HOW IZ I":
                self.parse_function_def()
                
            # <function_call>
            elif token_type == "FUNCTION_CALL" or (token_type == "I" and token_value == "IZ"):
                self.parse_function_call()
                
            # <input>
            elif token_type == "IO" and token_value == "GIMMEH":
                return self.parse_input()
                
            # <return>
            elif token_type == "RETURN" or (token_type == "FOUND" and token_value == "YR"):
                self.parse_return()
                
            # <exit>
            elif token_type == "EXIT" or (token_type == "GTFO"):
                self.advance()  # just consume GTFO
            
            # <typecast>  
            elif token_type == "TYPECAST" and token_value == "MAEK":
                self.parse_typecast()
                
            # <exeception_handling>
            elif token_type == "EXCEPTION" and token_value == "PLZ":
                self.parse_exception_handling()
                
            else:
                raise ParserError(f"Unknown statement starting with {token_type} {token_value}")
                error_msg = f"[Line {line}] Unknown statement starting with {token_type} {token_value}"
                self.errors.append(error_msg)
                self.advance()  # skip the token and continue
        
        except ParserError as e:
            # Collect parser errors instead of stopping
            self.errors.append(f"[Line {line}] {str(e)}")
            self.advance()              # Skip problematic token to continue
    # --------------------------
    # Specific Statement Parsers
    # --------------------------
    
    # <print> ::= VISIBLE <expr_list>
    def parse_print(self):
        self.expect("OUTPUT_KEYWORD", "VISIBLE")
        
        # Optional expression list
        token_type, token_value, *_ = self.current()
        if token_type in ("INT_LITERAL", "FLOAT_LITERAL", "STRING", "BOOL_TRUE", "BOOL_FALSE", "IDENTIFIER") \
        or token_value in ("SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "BIGGR OF", "SMALLR OF", "BOTH SAEM", "DIFFRINT", "SMOOSH"):
            self.parse_expr_list() 
            
    # <declaration> ::= I HAS A <varident> (ITZ <expr>)?
    def parse_declaration(self):
        self.expect("VAR_DECLARATION")
        self.expect("IDENTIFIER")
        if self.match("VAR_ASSIGNMENT"):
            self.parse_expr()
    
    # <assignment> ::= <varident> R <expr>
    def parse_assignment(self):
        self.expect("IDENTIFIER")
        if self.match("VAR_ASSIGNMENT"):
            self.parse_expr()
        else:
            # Possibly a function call
            if self.current()[0] == "FUNCTION_CALL":
                self.parse_function_call()
                
    # <return> ::= FOUND YR <expr>
    def parse_return(self):
        self.expect("RETURN", "FOUND YR")
        self.parse_expr()
        
    # <exit> ::= GTFO
    def parse_exit(self):
        self.expect("EXIT", "GTFO")
        
    # <typecast> ::= MAEK <expr> A <type>
    def parse_typecast(self):
        self.expect("TYPECAST", "MAEK")
        self.parse_expr()
        self.expect("A")
        self.expect("TYPE_LITERAL")
    
    # <conditional>  ::= O RLY? <linebreak> YA RLY <linebreak> <block>
    #               (MEBBE <expr> <linebreak> <block>)*
    #               (NO WAI <linebreak> <block>)?
    #               OIC
    def parse_conditional(self):
        self.expect("CONTROL_FLOW", "O RLY?")       # O RLY?
        self.expect("CONTROL_FLOW", "YA RLY")       # YA RLY
        self.parse_statement_list()                 # ()
        while self.match("CONTROL_FLOW", "MEBBE"):  # MEBBE
            self.parse_expr()
            self.parse_statement_list()
        if self.match("CONTROL_FLOW", "NO WAI"):    # NO WAI
            self.parse_statement_list()
        self.expect("CONTROL_FLOW", "OIC")          # OIC
    
    # <loop> ::= IM IN YR <loopident> [UPPIN|NERFIN] YR <varident> TIL <expr> <linebreak> <block> IM OUTTA YR <loopident>
    def parse_loop(self):
        self.expect("LOOPING", "IM IN YR")    
        self.expect("IDENTIFIER")                   # Loop identifier
        self.expect("YR")                       
        self.expect("IDENTIFIER")                   # Target variable
        self.expect("TIL")                    
        self.parse_expr()
        self.parse_statement_list()
        self.expect("LOOPING", "IM OUTTA YR")     
        self.expect("IDENTIFIER")             
        
    # <switch> ::= <expr> <linebreak> WTF? <linebreak> (OMG <literal> <linebreak> <statement_list>)* [OMGWTF <linebreak> <statement_list>] OIC
    def parse_switch(self):
        self.parse_expr()
        self.expect("SWITCH", "WTF?")
        while self.match("SWITCH_CASE", "OMG"):     # Parse case blocks
            self.parse_literal()
            self.parse_statement_list()
        if self.match("SWITCH_CASE", "OMGWTF"):     # Optional default case
            self.parse_statement_list()
        self.expect("CONTROL_FLOW", "OIC")
    
    # <function_def> ::= HOW IZ I <funcident> (<param>)* <linebreak> <block> IF U SAY SO
    def parse_function_def(self):
        self.expect("FUNCTION_DEF_CALL", "HOW IZ I")
        self.expect("IDENTIFIER")                   # Function name
        while self.match("YR"):
            self.expect("IDENTIFIER")               # Function args
        self.parse_statement_list()
        self.expect("FUNCTION_DEF_CALL", "IF U SAY SO")
    
    # <function_call>::= I IZ <funcident> (<expr>)* MKAY
    def parse_function_call(self):
        self.expect("FUNCTION_CALL")
        self.expect("IDENTIFIER")                   # Function name
        while self.match("YR"):
            self.parse_expr()
        self.expect("FUNCTION_END")
        
    # <input> ::= GIMMEH <varident>
    def parse_input(self):
        self.expect("INPUT")
        
        self.expect("IO", "GIMMEH")
        var_token = self.expect("IDENTIFIER")
        self.expect(f"VAR({var_token['value']})")
    
    # <exception_handling> ::= PLZ <expr>? <linebreak> AWSUM THX <linebreak> <statement_list> (O NOES <linebreak> <statement_list>)? KTHX
    def parse_exception_handling(self):
        self.expect("EXCEPTION", "PLZ")
        if self.current()[0] != "AWSUM THX":
            self.parse_expr()
        self.expect("EXCEPTION", "AWSUM THX")
        self.parse_statement_list()
        if self.match("EXCEPTION", "O NOES"):
            self.parse_statement_list()
        self.expect("EXCEPTION", "KTHX")
        
    # <block> ::= <statement_list>
    def parse_block(self):
        self.parse_statement_list()
    
    # -------------------------
    # Expressions
    # -------------------------
    def parse_expr_list(self):
        # <expr_list> ::= <expr> (YR <expr>)*
        token_type, token_value, *_ = self.current()
        
        # Only parse if next token is a valid expression start
        if token_type in ("INT_LITERAL", "FLOAT_LITERAL", "STRING", "BOOL_TRUE", "BOOL_FALSE", "IDENTIFIER") \
        or token_value in ("SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "BIGGR OF", "SMALLR OF", "BOTH SAEM", "DIFFRINT", "SMOOSH", "FUNCTION_CALL"):
            self.parse_expr()
            while self.match("YR"):
                self.parse_expr()
    
    def parse_expr(self):
        token_type, token_value, *_ = self.current()
        
        try:
            # Literal or variable
            if token_type in ("INT_LITERAL", "FLOAT_LITERAL", "STRING", "BOOL_TRUE", "BOOL_FALSE", "IDENTIFIER"):
                self.advance()
            
            # Arithmetic operation (SUM OF, DIFF OF, etc.)
            elif token_type == "ARITHMETIC_OPERATOR" or token_value in ("SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "BIGGR OF", "SMALLR OF"):
                self.parse_operation()
            
            # Comparison (BOTH SAEM, DIFFRINT)
            elif token_type == "COMPARISON_OPERATOR":
                self.parse_comparison()
            
            # SMOOSH concatenation
            elif token_type == "SMOOSH":
                self.parse_smoosh()
            
            # Function call
            elif token_type == "FUNCTION_CALL":
                self.parse_function_call()
                        
            else:
                raise ParserError(f"Unexpected token in expression: {token_type} {token_value}")

        except ParserError as e:
            self.errors.append(str(e))
            self.advance()  # Try to skip token and continue
    '''
    THIS NEEDS SOME FIXING:
    '''
    def parse_operation(self):
        # <operation> ::= SUM OF <expr> AN <expr> (AN <expr>)*
        self.advance()  # consume the operator keyword (SUM OF, DIFF OF, etc.)
        
        # Parse all operands recursively
        self.parse_expr()

        # additional operands (optional)
        while self.match("MULTI_PARAM_SEPARATOR", "AN"):
            self.parse_expr()


    def parse_comparison(self):
        self.advance()  # consume BOTH_SAEM or DIFFRINT

        # first operand
        self.parse_expr()

        # allow optional AN
        if self.match("MULTI_PARAM_SEPARATOR", "AN"):
            pass

        # second operand: check if there is a valid operand
        token_type, token_value, *_ = self.current()
        if token_type in (
            "INT_LITERAL", "FLOAT_LITERAL", "STRING", "BOOL_TRUE", "BOOL_FALSE",
            "IDENTIFIER", "ARITHMETIC_OPERATOR", "COMPARISON_OPERATOR", "SMOOSH"
        ):
            self.parse_expr()
        else:
            # second operand missing: assume simple comparison with only one operand
            return


    def parse_smoosh(self):
        # <smoosh> ::= SMOOSH <expr> (AN <expr>)*
        self.expect("SMOOSH")
        self.parse_expr()
        
        while self.match("MULTI_PARAM_SEPARATOR", "AN"):
            self.parse_expr()
            
    # -------------------------
    # Literals
    # -------------------------
    def parse_literal(self):
        token_type, *_ = self.current()
        if token_type in ("INT_LITERAL", "FLOAT_LITERAL", "STRING", "BOOL_TRUE", "BOOL_FALSE"):
            self.advance()
        else:
            raise ParserError(f"Expected literal, got {token_type}")
        
    # ------------------------- 
    # Helpers
    # -------------------------
    def check(self, ttype, value=None):
        token_type, token_value, *_ = self.current()
        return token_type == ttype and (value is None or token_value == value)
    
    def previous(self):
        if self.pos > 0:
            t = self.tokens[self.pos - 1]
            return {"type": t[0], "value": t[1]}
        return None
    
# -------------------------
# Validation helpers
# -------------------------
def validate_code(code: str):
    try:
        tokens = tokenize(code)
        parser = Parser(tokens)
        parser.parse_program()
        return []  # no syntax errors
    except ParserError as e:
        return [f"Line {e.line}: {str(e)}"]

def validate_file(filepath: str):
    try:
        with open(filepath, "r") as f:
            code = f.read()
        return validate_code(code)
    except FileNotFoundError:
        return [f"File not found: {filepath}"]
