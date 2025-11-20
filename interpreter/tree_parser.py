'''
This is a recursive-descent parser that generates an Abstract Syntax Tree (AST) for a LOLCODE program.
'''

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
        self.errors = []  # Collect parsing errors

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
            # Record error
            self.errors.append(
                f"Expected {ttype} {value}, got {token_type} {token_value} at position {self.pos}"
            )
            # Attempt recovery: skip current token
            self.advance()
            return {"type": token_type, "value": token_value}  # Still return something
        self.advance()
        return {"type": token_type, "value": token_value}
    
    # Return the next token type and value without advancing
    def peek_next(self):
        if self.pos + 1 < len(self.tokens):
            t = self.tokens[self.pos + 1]
            
            # Allow either (type,value) or (type,value,line,col)
            if isinstance(t, tuple):
                if len(t) >= 2:
                    return t[0], t[1]
            return None, None
        return None, None
    
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
            
            # End of program/block
            if token_type in (None, "CODE_DELIMITER", "OIC", "IF U SAY SO",
                       "IM OUTTA YR", "O NOES"):
                break
            
            # Handle WAZZUP/BUHBYE for variable declarations
            if token_type == "VAR_LIST_DELIMITER":
                if token_value == "WAZZUP":
                    self.in_wazzup = True
                    self.advance()
                    continue  # skip this token
                elif token_value == "BUHBYE":
                    self.in_wazzup = False
                    self.advance()
                    continue  # skip this token
                
            # Parse statement
            stmt = self.parse_statement()
            if stmt:
                node.add(stmt)
                
        return node

    # STATEMENT
    def parse_statement(self):
        token_type, token_value = self.current()

        # <print>
        if token_type == "OUTPUT_KEYWORD":
            return self.parse_print()
        
        # <declaration>
        elif token_type == "VAR_DECLARATION":
            
            # Enforce WAZZUP-only rule:
            if not getattr(self, "in_wazzup", False):
                self.errors.append(f"[pos {self.pos}] Variable declaration outside WAZZUP")
            return self.parse_declaration()

        # <identifier>
        elif token_type == "IDENTIFIER":
            next_type, next_value = self.peek_next()
            
            if next_type == "VAR_ASSIGNMENT":
                return self.parse_assignment()
            
            elif next_type == "IS_NOW_A":
                return self.parse_typecast()
            
            else:
                expr_node = self.parse_expr()
                node = TreeNode("EXPR_STMT")
                node.add(expr_node)
                return node
        
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
        
        # Arithmetic operation line
        elif token_type == "ARITHMETIC_OPERATOR":
            expr = self.parse_expr()
            node = TreeNode("EXPR_STMT")
            node.add(expr)
            return node

        # <input>
        elif token_type == "IO" and token_value == "GIMMEH":
            return self.parse_input()
            
        # <return>
        elif token_type == "RETURN" or (token_type == "FOUND" and token_value == "YR"):
            return self.parse_return()
            
        # <exit>
        elif token_type in ("EXIT", "GTFO"):
            self.advance()
            return TreeNode("EXIT")
                
        # <typecast>
        elif token_type == "MAEK" or (token_type == "IDENTIFIER" and self.peek_next()[0] == "IS_NOW_A"):
            node = self.parse_typecast()
            node = TreeNode("EXPR_STMT")
            node.add(self.parse_typecast())
            return node
        
        #elif token_type == "MAEK":
        #    expr_node = self.parse_typecast()
        #    node = TreeNode("EXPR_STMT")
        #    node.add(expr_node)
        #    return node
        
        # <exeception_handling>
        elif token_type == "EXCEPTION" and token_value == "PLZ":
            return self.parse_exception_handling()
        
        # Expression-only lines (EXPR_STMT)
        elif token_type in ("INT_LITERAL", "FLOAT_LITERAL", "STRING", "IDENTIFIER", "MAEK", "BOOL_TRUE", "BOOL_FALSE", "SMOOSH", "ARITHMETIC_OPERATOR"):
            expr = self.parse_expr()
            node = TreeNode("EXPR_STMT")
            node.add(expr)
            return node

        # Unknown / error
        else:
            self.errors.append(
                f"Unknown statement starting with {token_type} {token_value} at position {self.pos}"
            )
            self.advance()              # Skip token to try to continue parsing
            return TreeNode("ERROR")    # Create placeholder node

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

        # Variable name
        var_token = self.expect("IDENTIFIER")
        var_node = TreeNode("IDENTIFIER", var_token['value'], var_token.get('line'))
        node.add(var_node)

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
        ident_node = TreeNode("IDENTIFIER", ident['value'], ident.get('line'))
        node.add(ident_node)

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
        found_token = self.expect("RETURN_KEYWORD")  # should correspond to FOUND
        node.add(TreeNode("FOUND", found_token["value"], found_token.get('line')))
        
        # YR
        yr_token = self.expect("YR")
        node.add(TreeNode("YR", yr_token["value"], yr_token.get('line')))

        # Expression to return
        expr_node = self.parse_expr()
        node.add(expr_node)

        return node
    
    # <exit> ::= GTFO
    def parse_exit(self):
        gtfo_token = self.expect("EXIT_KEYWORD")  # token for GTFO
        node = TreeNode("EXIT", gtfo_token["value"], gtfo_token.get('line'))
        return node
    
    # <typecast> ::= MAEK <expr> A <type>
    def parse_typecast(self):
        node = TreeNode("TYPECAST")
        token_type, token_value = self.current()

        # Case 1: x IS NOW A NUMBAR
        if token_type == "IDENTIFIER":
            var_token = self.expect("IDENTIFIER")
            node.add(TreeNode("VAR", var_token["value"], var_token.get('line')))
            
            if self.match("IS_NOW_A"):
                # TYPE_LITERAL is required
                type_token = self.expect("TYPE_LITERAL")
                node.add(TreeNode("TYPE", type_token["value"], type_token.get('line')))
                return node
            else:
                # recovery: we expected IS NOW A but didn't get it
                self.errors.append(f"[pos {self.pos}] Expected IS NOW A after {var_token['value']}")
                return node

        # Case 2: MAEK expr A TYPE
        elif token_type == "MAEK":
            # consume MAEK
            maek_token = self.expect("MAEK")
            node.add(TreeNode("MAEK", maek_token["value"], maek_token.get('line')))

            # parse the inner expression to be cast
            expr_node = self.parse_expr()
            node.add(expr_node)
            
            if self.current()[0] == "A":
                self.expect("A")

            # Type literal required
            type_token = self.expect("TYPE_LITERAL")
            node.add(TreeNode("TYPE", type_token["value"], type_token.get('line')))

            return node

        else:
            self.errors.append(f"[pos {self.pos}] Invalid typecast start: {token_type} {token_value}")
            self.advance()
        
        return node
    
    # <conditional>  ::= O RLY? <linebreak> YA RLY <linebreak> <block>
    #               (MEBBE <expr> <linebreak> <block>)*
    #               (NO WAI <linebreak> <block>)?
    #               OIC
    def parse_conditional(self):
        node = TreeNode("IF")

        # O RLY?
        orly_token = self.expect("ORLY")
        node.add(TreeNode("ORLY", orly_token["value"], orly_token.get('line')))

        # YA RLY
        yarly_token = self.expect("YARLY")
        ya_block = self.parse_block()
        ya_node = TreeNode("YA_RLY", yarly_token["value"], yarly_token.get('line'))
        ya_node.add(ya_block)
        node.add(ya_node)

        # optional: any number of MEBBE <expr> <block>
        while self.match("MEBBE"):
            mebbe_token = self.previous()
            expr = self.parse_expr()
            block = self.parse_block()
            mebbe_node = TreeNode("MEBBE", mebbe_token["value"], mebbe_token.get('line'))
            mebbe_node.add(expr)
            mebbe_node.add(block)
            node.add(mebbe_node)

        # optional NO WAI
        if self.match("NOWAI"):
            nowai_token = self.previous()
            no_block = self.parse_block()
            no_node = TreeNode("NO_WAI", nowai_token["value"], nowai_token.get('line'))
            no_node.add(no_block)
            node.add(no_node)

        # OIC
        oic_token = self.expect("OIC")
        node.add(TreeNode("OIC", oic_token["value"], oic_token.get('line')))

        return node
    
    # <loop> ::= IM IN YR <loopident> [UPPIN|NERFIN] YR <varident> TIL <expr> <linebreak> <block> IM OUTTA YR <loopident>
    def parse_loop(self):
        node = TreeNode("LOOP")

        im_token = self.expect("IMINYR")
        node.add(TreeNode("IMINYR", im_token["value"], im_token.get('line')))
    
        loop_name_token = self.expect("IDENTIFIER")
        node.add(TreeNode("LOOP_NAME", loop_name_token["value"], loop_name_token.get('line')))

        # Optional UPPIN/NERFIN
        if self.match("UPPIN", "NERFIN"):
            direction_token = self.previous()
            self.expect("YR")
            var_token = self.expect("IDENTIFIER")
            
            dir_node = TreeNode("DIRECTION")
            dir_node.add(TreeNode("OP", direction_token["value"], direction_token.get('line')))
            dir_node.add(TreeNode("VAR", var_token["value"], var_token.get('line')))
            node.add(dir_node)

        self.expect("TIL")
        cond_expr = self.parse_expr()
        node.add(cond_expr)

        # Loop block
        block = self.parse_block()
        node.add(block)

        # Loop exit
        self.expect("IMOUTTAYR")
        end_name_token = self.expect("IDENTIFIER")
        node.add(TreeNode("LOOP_END", end_name_token["value"], end_name_token.get('line')))

        return node

    # <switch> ::= <expr> <linebreak> WTF? <linebreak> (OMG <literal> <linebreak> <statement_list>)* [OMGWTF <linebreak> <statement_list>] OIC
    def parse_switch(self):
        node = TreeNode("SWITCH")

        expr = self.parse_expr()
        node.add(expr)

        wtf_token = self.expect("WTF")
        node.add(TreeNode("WTF", wtf_token["value"], wtf_token.get('line')))

        # OMG cases
        while self.match("OMG"):
            omg_token = self.previous()
            literal = self.parse_literal()
            block = self.parse_block()

            case_node = TreeNode("CASE", omg_token["value"], omg_token.get('line'))
            case_node.add(literal)
            case_node.add(block)
            node.add(case_node)

        # Optional OMGWTF default case
        if self.match("OMGWTF"):
            omgwtf_token = self.previous()
            block = self.parse_block()
            default_node = TreeNode("DEFAULT", omgwtf_token["value"], omgwtf_token.get('line'))
            default_node.add(block)
            node.add(default_node)

        oic_token = self.expect("OIC")
        node.add(TreeNode("OIC", oic_token["value"], oic_token.get('line')))

        return node

    # <function_def> ::= HOW IZ I <funcident> (<param>)* <linebreak> <block> IF U SAY SO
    def parse_function_def(self):
        node = TreeNode("FUNC_DEF")

        # HOW IZ I
        howizi_token = self.expect("HOWIZI")
        node.add(TreeNode("HOWIZI", howizi_token["value"], howizi_token.get('line')))

        # function name
        func_name = self.expect("IDENTIFIER")
        node.add(TreeNode("FUNC_NAME", func_name["value"], func_name.get('line')))

        # Parameters: 0 or more "YR <IDENTIFIER>"
        params_node = TreeNode("PARAMS")
        while self.match("YR"):
            yr_token = self.previous()
            param = self.expect("IDENTIFIER")
            params_node.add(TreeNode("PARAM", param["value"], param.get('line')))
        node.add(params_node)

        # Block
        block = self.parse_block()
        node.add(block)

        # IF U SAY SO
        ifusayso_token = self.expect("IFUSAYSO")
        node.add(TreeNode("IFUSAYSO", ifusayso_token["value"], ifusayso_token.get('line')))

        return node
    
    # <function_call>::= I IZ <funcident> (<expr>)* MKAY
    def parse_function_call(self):
        node = TreeNode("FUNC_CALL")

        # I IZ
        iiz_token = self.expect("I IZ")
        node.add(TreeNode("IIZ", iiz_token["value"], iiz_token.get('line')))

        # function name
        func_name = self.expect("IDENTIFIER")
        node.add(TreeNode("FUNC_NAME", func_name["value"], func_name.get('line')))
    
        # arguments
        args_node = TreeNode("ARGS")
        while self.match("YR"):
            yr_token = self.previous()
            expr = self.parse_expr()
            expr_node = TreeNode("ARG", None, yr_token.get('line'))
            expr_node.add(expr)
            args_node.add(expr_node)
        node.add(args_node)

        # MKAY
        mkay_token = self.expect("MKAY")
        node.add(TreeNode("MKAY", mkay_token["value"], mkay_token.get('line')))

        return node
    
    # <input> ::= GIMMEH <varident>
    def parse_input(self):
        node = TreeNode("INPUT")
        
        # GIMMEH keyword
        gimmeh_token = self.expect("IO", "GIMMEH")
        node.add(TreeNode("GIMMEH", gimmeh_token["value"], gimmeh_token.get('line')))
        
        # Variable
        var_token = self.expect("IDENTIFIER")
        node.add(TreeNode("VAR", var_token["value"], var_token.get('line')))
        
        return node
        
    # <exception_handling> ::= PLZ <expr>? <linebreak> AWSUM THX <linebreak> <statement_list> (O NOES <linebreak> <statement_list>)? KTHX
    def parse_exception_handling(self):
        node = TreeNode("EXCEPTION")

        # PLZ
        plz_token = self.expect("PLZ")
        node.add(TreeNode("PLZ", plz_token["value"], plz_token.get('line')))
        
        # optional <expr>
        if not self.check("AWSUMTHX"):
            expr = self.parse_expr()
            node.add(expr)
        
        # AWSUM THX
        aws_token = self.expect("AWSUMTHX")
        
        # success block
        success_block = self.parse_block()
        success_node = TreeNode("SUCCESS", aws_token["value"], aws_token.get('line'))
        success_node.add(success_block)
        node.add(success_node)
        
        # optional O NOES
        if self.match("ONOES"):
            fail_token = self.previous()  # token for O NOES
            fail_block = self.parse_block()
            fail_node = TreeNode("FAIL", fail_token["value"], fail_token.get('line'))
            fail_node.add(fail_block)
            node.add(fail_node)
        
        # KTHX
        kthx_token = self.expect("KTHX")
        node.add(TreeNode("KTHX", kthx_token["value"], kthx_token.get('line')))
        
        return node

    # <block> ::= <statement_list>
    def parse_block(self):
        block_node = TreeNode("BLOCK")
        stmt_list_node = self.parse_statement_list()
        block_node.add(stmt_list_node)
        return block_node


    # -------------------------
    # Expressions
    # -------------------------
    def parse_expr_list(self):
        node = TreeNode("EXPR_LIST")
        expr_node = self.parse_expr()
        node.add(expr_node)
        
        while self.match("YR"):
            expr_node = self.parse_expr()
            node.add(expr_node)
        
        return node

    # EXPR
    def parse_expr(self):
        token_type, token_value = self.current()

        # Literal or variable
        if token_type in ("INT_LITERAL", "FLOAT_LITERAL", "STRING", "BOOL_TRUE", "BOOL_FALSE"):
            self.advance()
            return TreeNode("LITERAL", token_value, getattr(self.current(), 'line', None))
        
        # Identifiers
        elif token_type == "IDENTIFIER":
            self.advance()
            return TreeNode("IDENTIFIER", token_value, getattr(self.current(), 'line', None))
        
        # Typecast expressions
        elif token_type == "MAEK":
            return self.parse_typecast()

        # Arithmetic operation (SUM OF, DIFF OF, etc.)
        elif token_type == "ARITHMETIC_OPERATOR" or token_value in ("SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "BIGGR OF", "SMALLR OF", "MOD OF"):
            return self.parse_operation()
        
        # Comparison (BOTH SAEM, DIFFRINT)
        elif token_type == "COMPARISON_OPERATOR":
            return self.parse_comparison()
        
        # Logical (BOTH OF, ANY OF, ALL OF, etc.)
        elif token_type == "LOGICAL_OPERATOR":
            if token_value == "NOT":
                self.advance()
                node = TreeNode("NOT", token_value, getattr(self.current(), 'line', None))
                node.add(self.parse_expr())
                return node
            else:
                return self.parse_logical()
        
        # SMOOSH concatenation
        elif token_type == "SMOOSH":
            return self.parse_smoosh()
        
        # Function call
        elif token_type == "FUNCTION_CALL":
            return self.parse_function_call()

        else:
            #raise ParserError(f"Unexpected token in expression: {token_type} {token_value}")
            self.errors.append(f"Unexpected token {token_type} {token_value} at pos {self.pos}")
            self.advance()
            return TreeNode("ERROR", token_value, getattr(self.current(), 'line', None))
        
    def parse_operation(self):
        # Get operator token
        tok = self.expect("ARITHMETIC_OPERATOR")
        token_type = tok["type"]
        token_value = tok["value"]
        line = tok.get('line')

        # Create operation node
        node = TreeNode("OP", token_value, line)
        
        # FIRST operand
        left = self.parse_expr()
        node.add(left)
        
        # Additional operands separated by AN
        while self.match("MULTI_PARAM_SEPARATOR", "AN"):
            right = self.parse_expr()
            node.add(right)

        # Expect AN
        # self.current()[0] == "MULTI_PARAM_SEPARATOR":
        #    self.expect("MULTI_PARAM_SEPARATOR")  # AN
        #    right = self.parse_expr()
        #    node.add(right)
        #else:
        #    raise ParserError(f"Expected AN in arithmetic operation: {token_type} {token_value}")

        return node
    
    def parse_comparison(self):
        # Get the comparison operator token
        token_type, token_value = self.current()
        line = self.tokens[self.pos][2] if len(self.tokens[self.pos]) > 2 else None
        self.advance()
        
        # Create comparison node
        node = TreeNode("COMPARISON", token_value, line)

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
    
    def parse_logical(self):
        token_type, token_value = self.current()
        line = self.tokens[self.pos][2] if len(self.tokens[self.pos]) > 2 else None
        
        # Combine ANY/ALL with OF if necessary
        if token_value in ("ANY", "ALL"):
            self.advance()
            next_type, next_value = self.current()
            if next_type == "LOGICAL_OPERATOR" and next_value == "OF":
                token_value = f"{token_value} OF"
                self.advance()
            else:
                raise ParserError(f"Expected OF after {token_value}")

        else:
            self.advance()

        # Create node with value and line
        node = TreeNode("LOGICAL", token_value, line)

        if token_value == "NOT":
            node.add(self.parse_expr())
            return node
        elif token_value in ("BOTH OF", "EITHER OF", "WON OF"):
            node.add(self.parse_expr())
            self.expect("MULTI_PARAM_SEPARATOR", "AN")
            node.add(self.parse_expr())
            return node
        elif token_value in ("ALL OF", "ANY OF"):
            node.add(self.parse_expr())
            while self.match("MULTI_PARAM_SEPARATOR", "AN"):
                node.add(self.parse_expr())
            self.expect("FUNCTION_DEF_CALL", "MKAY")
            return node
        else:
            self.errors.append(f"Unknown logical operator: {token_value}")
            return node
    
    # <smoosh> ::= SMOOSH <expr> (AN <expr>)*
    def parse_smoosh(self):    
        
        token_type, token_value = self.current()
        line = self.tokens[self.pos][2] if len(self.tokens[self.pos]) > 2 else None
    
        # Consume SMOOSH
        self.expect("SMOOSH")
        
        # Create SMOOSH node
        node = TreeNode("SMOOSH", token_value, line)

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
        line = self.tokens[self.pos][2] if len(self.tokens[self.pos]) > 2 else None
        
        if token_type in ("INT_LITERAL", "FLOAT_LITERAL", "STRING", "BOOL_TRUE", "BOOL_FALSE"):
            self.advance()
            return TreeNode("LITERAL", token_value, line)
        else:
            raise ParserError(f"Expected literal, got {token_type} ({token_value})")

    # ------------------------- 
    # Helpers
    # -------------------------
    def check(self, ttype, value=None):
        token_type, token_value = self.current()
        return token_type == ttype and (value is None or token_value == value)
    
    def previous(self):
        if self.pos > 0:
            t = self.tokens[self.pos - 1]
            return {"type": t[0], "value": t[1], 'line': t[2] if len(t) > 2 else None}
        return None
