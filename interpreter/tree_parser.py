from lexer import tokenize
from parser import ParserError   # reuse your error class
from tree_node import TreeNode   # the class above

# -------------------------
# Tree Parser
# -------------------------
class TreeParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # helpers
    def current(self):
        if self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            return t[0], t[1]
        return None, None

    def advance(self):
        self.pos += 1

    def match(self, ttype, value=None):
        token_type, token_value = self.current()
        if token_type == ttype and (value is None or token_value == value):
            self.advance()
            return True
        return False

    def expect(self, ttype, value=None):
        token_type, token_value = self.current()
        if token_type != ttype or (value is not None and token_value != value):
            raise ParserError(f"Expected {ttype} {value}, got {token_type} {token_value}")
        self.advance()
        return {"type": token_type, "value": token_value}
    
    # -------------------------
    # Program Entry
    # -------------------------
    # PROGRAM ::= HAI stmt_list KTHXBYE
    def parse_program(self):
        node = TreeNode("PROG")
        self.expect("CODE_DELIMITER", "HAI")
        node.add(TreeNode("HAI"))

        node.add(self.parse_statement_list())

        self.expect("CODE_DELIMITER", "KTHXBYE")
        node.add(TreeNode("KTHXBYE"))
        return node

    # -------------------------
    # Statement Parsing
    # -------------------------
    def parse_statement_list(self):
        node = TreeNode("STMT_LIST")
        while True:
            token_type, token_value = self.current()
            if token_type in (None, "CODE_DELIMITER", "OIC", "IF U SAY SO",
                       "IM OUTTA YR", "O NOES"):
                break
            if token_type == "VAR_LIST_DELIMITER":
                self.advance()
                continue
            node.add(self.parse_statement())
        return node

    # STATEMENT
    def parse_statement(self):
        token_type, token_value = self.current()

        # <print>
        if token_type == "OUTPUT_KEYWORD":
            return self.parse_print()
        
        # <declaration>
        elif token_type == "VAR_DECLARATION":
            return self.parse_declaration()

        # <identifier>
        elif token_type == "IDENTIFIER":
            return self.parse_assignment()
        
        # <conditional>
        elif token_type == "CONTROL_FLOW" and token_value == "O RLY?":
            return self.parse_conditional()
        
        # <loop>
        elif token_type == "LOOPING" and token_value == "IM IN YR":
            return self.parse_loop()
            
        # <function_def>
        elif token_type == "FUNCTION_DEF_CALL" and token_value == "HOW IZ I":
            return self.parse_function_def()
            
        # <function_call>
        elif token_type == "FUNCTION_CALL" or (token_type == "I" and token_value == "IZ"):
            return self.parse_function_call()
            
        # <return>
        elif token_type == "RETURN" or (token_type == "FOUND" and token_value == "YR"):
            return self.parse_return()
            
        # <exit>
        elif token_type in ("EXIT", "GTFO"):
            self.advance()
            return TreeNode("EXIT")
                
        # <typecast>  
        elif token_type == "TYPECAST" and token_value == "MAEK":
            return self.parse_typecast()
            
        # <exeception_handling>
        elif token_type == "EXCEPTION" and token_value == "PLZ":
            return self.parse_exception_handling()

        else:
            raise ParserError(f"Unknown statement starting with {token_type} {token_value}")

    # --------------------------
    # Specific Statement Parsers
    # --------------------------
    
    # PRINT ::= VISIBLE expr_list
    def parse_print(self):
        node = TreeNode("PRINT")
        
        self.expect("OUTPUT_KEYWORD", "VISIBLE")
        
        node.add(TreeNode("VISIBLE"))
        node.add(self.parse_expr_list())
        
        return node
    
    # <declaration> ::= I HAS A <varident> (ITZ <expr>)?
    def parse_declaration(self):
        node = TreeNode("VAR_DEC")

        # I HAS A
        self.expect("VAR_DECLARATION")

        # variable name
        var_token = self.expect("IDENTIFIER")
        node.add(TreeNode(f"VAR({var_token['value']})"))

        # Optional: ITZ <expr>
        if self.match("VAR_ASSIGNMENT"):
            expr_node = self.parse_expr()
            node.add(expr_node)

        return node

    # <assignment> ::= <varident> R <expr>
    def parse_assignment(self):
        node = TreeNode("ASSIGN")
        
        # IDENTIFIER
        ident = self.expect("IDENTIFIER")
        node.add(TreeNode(f"IDENTIFIER({ident['value']})"))

        # R keyword
        self.expect("VAR_ASSIGNMENT")

        # expr
        expr_node = self.parse_expr()
        node.add(expr_node)
        return node
    
    # <return> ::= FOUND YR <expr>
    def parse_return(self):
        node = TreeNode("RETURN")

        # FOUND
        self.expect("RETURN_KEYWORD")  # should correspond to FOUND
        # YR
        self.expect("YR")

        expr_node = self.parse_expr()
        node.add(expr_node)

        return node
    
    # <exit> ::= GTFO
    def parse_exit(self):
        node = TreeNode("EXIT")
        self.expect("EXIT_KEYWORD")  # token for GTFO
        return node
    
    # <typecast> ::= MAEK <expr> A <type>
    def parse_typecast(self):
        node = TreeNode("TYPECAST")

        # MAEK
        self.expect("TYPECAST_KEYWORD")

        # <expr>
        expr_node = self.parse_expr()
        node.add(expr_node)

        # A
        self.expect("A")

        # <type>
        type_tok = self.expect("TYPE_LITERAL")
        node.add(TreeNode(f"TYPE({type_tok['value']})"))

        return node
    
    # <conditional>  ::= O RLY? <linebreak> YA RLY <linebreak> <block>
    #               (MEBBE <expr> <linebreak> <block>)*
    #               (NO WAI <linebreak> <block>)?
    #               OIC
    def parse_conditional(self):
        node = TreeNode("IF")

        # O RLY?
        self.expect("ORLY")  

        # YA RLY
        self.expect("YARLY")
        ya_block = self.parse_block()
        node.add(TreeNode("YA_RLY"))
        node.add(ya_block)

        # optional: any number of MEBBE <expr> <block>
        while self.match("MEBBE"):
            expr = self.parse_expr()
            block = self.parse_block()
            mebbe_node = TreeNode("MEBBE")
            mebbe_node.add(expr)
            mebbe_node.add(block)
            node.add(mebbe_node)

        # optional: NO WAI
        if self.match("NOWAI"):
            no_block = self.parse_block()
            no_node = TreeNode("NO_WAI")
            no_node.add(no_block)
            node.add(no_node)

        # OIC
        self.expect("OIC")

        return node
    
    # <loop> ::= IM IN YR <loopident> [UPPIN|NERFIN] YR <varident> TIL <expr> <linebreak> <block> IM OUTTA YR <loopident>
    def parse_loop(self):
        node = TreeNode("LOOP")

        self.expect("IMINYR")   # IM IN YR
        loop_name = self.expect("IDENTIFIER")
        node.add(TreeNode(f"LOOP_NAME({loop_name['value']})"))

        # Optional UPPIN/NERFIN
        if self.match("UPPIN") or self.match("NERFIN"):
            direction = self.previous()  # last consumed token
            self.expect("YR")
            varname = self.expect("IDENTIFIER")
            dir_node = TreeNode("DIRECTION")
            dir_node.add(TreeNode(direction['value']))
            dir_node.add(TreeNode(varname['value']))
            node.add(dir_node)

        self.expect("TIL")
        cond_expr = self.parse_expr()
        node.add(cond_expr)

        # Loop block
        block = self.parse_block()
        node.add(block)

        # Loop exit
        self.expect("IMOUTTAYR")
        end_name = self.expect("IDENTIFIER")
        node.add(TreeNode(f"LOOP_END({end_name['value']})"))

        return node
    
    def previous(self):
        if self.pos > 0:
            return {"type": self.tokens[self.pos-1][0], "value": self.tokens[self.pos-1][1]}
        return None

    # <switch> ::= <expr> <linebreak> WTF? <linebreak> (OMG <literal> <linebreak> <statement_list>)* [OMGWTF <linebreak> <statement_list>] OIC
    def parse_switch(self):
        node = TreeNode("SWITCH")

        expr = self.parse_expr()
        node.add(expr)

        self.expect("WTF")

        # OMG cases
        while self.match("OMG"):
            literal = self.parse_literal()
            block = self.parse_block()

            case_node = TreeNode("CASE")
            case_node.add(literal)
            case_node.add(block)
            node.add(case_node)

        # Optional OMGWTF default case
        if self.match("OMGWTF"):
            block = self.parse_block()
            default_node = TreeNode("DEFAULT")
            default_node.add(block)
            node.add(default_node)

        self.expect("OIC")

        return node

    # <function_def> ::= HOW IZ I <funcident> (<param>)* <linebreak> <block> IF U SAY SO
    def parse_function_def(self):
        node = TreeNode("FUNC_DEF")

        # HOW IZ I
        self.expect("HOWIZI")

        # function name
        func_name = self.expect("IDENTIFIER")
        node.add(TreeNode(f"FUNC_NAME({func_name['value']})"))

        # Parameters: 0 or more "YR <IDENTIFIER>"
        params_node = TreeNode("PARAMS")
        while self.match("YR"):
            param = self.expect("IDENTIFIER")
            params_node.add(TreeNode(param['value']))
        node.add(params_node)

        # Block
        block = self.parse_block()
        node.add(block)

        # IF U SAY SO
        self.expect("IFUSAYSO")

        return node
    
    # <function_call>::= I IZ <funcident> (<expr>)* MKAY
    def parse_function_call(self):
        node = TreeNode("FUNC_CALL")

        # I IZ
        self.expect("IIZ")

        func_name = self.expect("IDENTIFIER")
        node.add(TreeNode(f"FUNC_NAME({func_name['value']})"))

        # arguments
        args_node = TreeNode("ARGS")
        while self.match("YR"):
            expr = self.parse_expr()
            args_node.add(expr)
        node.add(args_node)

        # MKAY
        self.expect("MKAY")

        return node

    # <exception_handling> ::= PLZ <expr>? <linebreak> AWSUM THX <linebreak> <statement_list> (O NOES <linebreak> <statement_list>)? KTHX
    def parse_exception_handling(self):
        node = TreeNode("EXCEPTION")

        # PLZ
        self.expect("PLZ")

        # optional <expr>
        if not self.check("AWSUMTHX"):
            expr = self.parse_expr()
            node.add(expr)

        # AWSUM THX
        self.expect("AWSUMTHX")

        # success block
        success_block = self.parse_block()
        success_node = TreeNode("SUCCESS")
        success_node.add(success_block)
        node.add(success_node)

        # optional O NOES
        if self.match("ONOES"):
            fail_block = self.parse_block()
            fail_node = TreeNode("FAIL")
            fail_node.add(fail_block)
            node.add(fail_node)

        # KTHX
        self.expect("KTHX")

        return node
    
    def check(self, ttype, value=None):
        token_type, token_value = self.current()
        return token_type == ttype and (value is None or token_value == value)

    # <block> ::= <statement_list>
    def parse_block(self):
        return self.parse_statement_list()


    # -------------------------
    # Expressions
    # -------------------------
    def parse_expr_list(self):
        node = TreeNode("EXPR_LIST")
        node.add(self.parse_expr())
        while self.match("YR"):
            node.add(self.parse_expr())
        return node

    # EXPR
    def parse_expr(self):
        token_type, token_value = self.current()

        # Literal or variable
        if token_type in ("INT_LITERAL", "FLOAT_LITERAL", "STRING", "BOOL_TRUE", "BOOL_FALSE"):
            return self.parse_literal()
        
        elif token_type == "IDENTIFIER":
            self.advance()
            return TreeNode(f"IDENTIFIER({token_value})")

        # Arithmetic operation (SUM OF, DIFF OF, etc.)
        elif token_type == "ARITHMETIC_OPERATOR" or token_value in ("SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "BIGGR OF", "SMALLR OF"):
            return self.parse_operation()
        
        # Comparison (BOTH SAEM, DIFFRINT)
        elif token_type == "COMPARISON_OPERATOR":
            return self.parse_comparison()
        
        # SMOOSH concatenation
        elif token_type == "SMOOSH":
            return self.parse_smoosh()
        
        # Function call
        elif token_type == "FUNCTION_CALL":
            return self.parse_function_call()

        else:
            raise ParserError(f"Unexpected token in expression: {token_type} {token_value}")

    def parse_operation(self):
        # Get operator token
        token_type, op = self.current()
        self.advance()

        # Create operation node
        node = TreeNode(f"OP({op})")
        
        # Determine if operator is binary or variadic
        binary_ops = ("BIGGR OF", "SMALLR OF")

        # First operand
        node.add(self.parse_expr())

        # Additional operands separated by AN
        while self.match("MULTI_PARAM_SEPARATOR", "AN"):
            node.add(self.parse_expr())

        return node
    
    def parse_comparison(self):
        # Get the comparison operator token
        token_type, op = self.current()
        self.advance()
        
        node = TreeNode(f"COMPARISON({op})")

        # First operand
        node.add(self.parse_expr())

        # Optional AN
        while self.match("MULTI_PARAM_SEPARATOR", "AN"):
            node.add(self.parse_expr())
        '''
        # Second operand (if valid)
        token_type, token_value = self.current()
        if token_type in (
            "INT_LITERAL", "FLOAT_LITERAL", "STRING", "BOOL_TRUE", "BOOL_FALSE",
            "IDENTIFIER", "ARITHMETIC_OPERATOR", "COMPARISON_OPERATOR", "SMOOSH"
        ):
            second_expr = self.parse_expr()
            node.add(second_expr)
        '''
        return node


    def parse_smoosh(self):
        # <smoosh> ::= SMOOSH <expr> (AN <expr>)*
        self.expect("SMOOSH")
        node = TreeNode("SMOOSH")

        # First expression
        first_expr = self.parse_expr()
        node.add(first_expr)

        # Additional expressions separated by AN
        while self.match("MULTI_PARAM_SEPARATOR", "AN"):
            expr = self.parse_expr()
            node.add(expr)

        return node
    
    # -------------------------
    # Literals
    # -------------------------
    def parse_literal(self):
        token_type, token_value = self.current()
        if token_type in ("INT_LITERAL", "FLOAT_LITERAL", "STRING", "BOOL_TRUE", "BOOL_FALSE"):
            self.advance()
            return TreeNode(f"LITERAL({token_value})")
        else:
            raise ParserError(f"Expected literal, got {token_type}")


