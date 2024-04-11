"""MyPL simple syntax checker (parser) implementation.

NAME: Lauren Nguyen
DATE: Spring 2024
CLASS: CPSC 326
"""

from mypl_error import *
from mypl_token import *
from mypl_lexer import *


class SimpleParser:

    def __init__(self, lexer):
        """Create a MyPL syntax checker (parser). 
        
        Args:
            lexer -- The lexer to use in the parser.

        """
        self.lexer = lexer
        self.curr_token = None

        
    def parse(self):
        """Start the parser."""
        self.advance()
        while not self.match(TokenType.EOS):
            if self.match(TokenType.STRUCT):
                self.struct_def()
            else:
                self.fun_def()
        self.eat(TokenType.EOS, 'expecting EOF')

        
    #----------------------------------------------------------------------
    # Helper functions
    #----------------------------------------------------------------------

    def error(self, message):
        """Raises a formatted parser error.

        Args:
            message -- The basic message (expectation)

        """
        lexeme = self.curr_token.lexeme
        line = self.curr_token.line
        column = self.curr_token.column
        err_msg = f'{message} found "{lexeme}" at line {line}, column {column}'
        raise ParserError(err_msg)


    def advance(self):
        """Moves to the next token of the lexer."""
        self.curr_token = self.lexer.next_token()
        # skip comments
        while self.match(TokenType.COMMENT):
            self.curr_token = self.lexer.next_token()

            
    def match(self, token_type):
        """True if the current token type matches the given one.

        Args:
            token_type -- The token type to match on.

        """
        return self.curr_token.token_type == token_type

    
    def match_any(self, token_types):
        """True if current token type matches on of the given ones.

        Args:
            token_types -- Collection of token types to check against.

        """
        for token_type in token_types:
            if self.match(token_type):
                return True
        return False

    
    def eat(self, token_type, message):
        """Advances to next token if current tokey type matches given one,
        otherwise produces and error with the given message.

        Args: 
            token_type -- The totken type to match on.
            message -- Error message if types don't match.

        """
        if not self.match(token_type):
            self.error(message)
        self.advance()

        
    def is_bin_op(self):
        """Returns true if the current token is a binary operation token."""
        ts = [TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE,
              TokenType.AND, TokenType.OR, TokenType.EQUAL, TokenType.LESS,
              TokenType.GREATER, TokenType.LESS_EQ, TokenType.GREATER_EQ,
              TokenType.NOT_EQUAL]
        return self.match_any(ts)

    
    #----------------------------------------------------------------------
    # Recursive descent functions
    #----------------------------------------------------------------------
        
    def struct_def(self):
        self.eat(TokenType.STRUCT, 'Expecting STRUCT Token Type')
        self.eat(TokenType.ID, 'Expecting ID Token Type')
        self.eat(TokenType.LBRACE, 'Expecting { Token Type')
        self.fields()
        self.eat(TokenType.RBRACE, 'Expecting } Token type')


        
    def fields(self):
        while(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.SEMICOLON) or self.match(TokenType.ID) or self.match(TokenType.ARRAY)):
            self.data_type()
            self.eat(TokenType.ID, 'Expecting ID TokenType')
            self.eat(TokenType.SEMICOLON, 'Expecting semicolon Token')
            
    def fun_def(self):
        if(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.SEMICOLON) or self.match(TokenType.ID) or self.match(TokenType.ARRAY)):
            self.data_type()
        elif(self.match(TokenType.VOID_TYPE)):
            self.eat(TokenType.VOID_TYPE, 'Expecting Void')


        self.eat(TokenType.ID, "Expecting ID Token type")
        self.eat(TokenType.LPAREN, 'Expecting ( Token type')
        self.params()
        self.eat(TokenType.RPAREN, 'Expecting ) Token type')
        self.eat(TokenType.LBRACE, "Expecting { Token Type")
        while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN)
                or self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) 
                or self.match(TokenType.SEMICOLON) or self.match(TokenType.ARRAY) or self.match(TokenType.ID) or self.match(TokenType.ASSIGN)):
                self.stmt()
        self.eat(TokenType.RBRACE, 'Expecting } Token type')

    def params(self):
        if(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.VOID_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.ARRAY) or self.match(TokenType.ID)):
            self.data_type()
            self.eat(TokenType.ID, 'Expected ID')
            while(self.match(TokenType.COMMA)):
                self.eat(TokenType.COMMA, 'Expecting comma')
                self.data_type()
                self.eat(TokenType.ID, 'Expecting ID')


    def data_type(self):
        if(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.STRING_TYPE)):
            self.base_type()
        elif(self.match(TokenType.ID)):
            self.eat(TokenType.ID, 'Expecting ID')
        elif(self.match(TokenType.ARRAY)):
            self.eat(TokenType.ARRAY, 'Expecting Array Value')
            if(self.match(TokenType.ID)):
                self.eat(TokenType.ID, 'Expecting ID')
            else:
                self.base_type()
            
    
    def base_type(self):
        if(self.match(TokenType.INT_TYPE)):
            self.advance()
            
        if(self.match(TokenType.DOUBLE_TYPE)):
            self.advance()
            
        if(self.match(TokenType.BOOL_TYPE)):
            self.advance()
            
        if(self.match(TokenType.STRING_TYPE)):
            self.advance()
        

    def stmt(self):
        if(self.match(TokenType.WHILE)):
            self.while_stmt()
        if(self.match(TokenType.IF)):
            self.if_stmt()
        if(self.match(TokenType.FOR)):
            self.for_stmt()
        if(self.match(TokenType.RETURN)):
            self.return_stmt()
            self.eat(TokenType.SEMICOLON, 'Expecting ;')
        if(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.SEMICOLON) or self.match(TokenType.ARRAY)):
            self.vdecl_stmnt()
            self.eat(TokenType.SEMICOLON, 'Expecting ;')
        if(self.match(TokenType.ID)):
            self.advance()
            if(self.match(TokenType.LPAREN)):
                self.call_expr()
            elif(self.match(TokenType.LBRACKET) or self.match(TokenType.DOT) or self.match(TokenType.ASSIGN)):
                self.assign_stmt()
            else:
                self.vdecl_stmnt()
            self.eat(TokenType.SEMICOLON, 'Expecting ;')
        

    def vdecl_stmnt(self):
        if(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.SEMICOLON) or self.match(TokenType.ARRAY)):
            self.data_type()
            self.eat(TokenType.ID, 'Expecting ID')
            if(self.match(TokenType.ASSIGN)):
                self.advance()
                self.expr()
        elif(self.match(TokenType.ID)):
            self.data_type()
            if(self.match(TokenType.ASSIGN)):
                self.advance()
                self.expr()

    def assign_stmt(self):
        self.lvalue()
        self.eat(TokenType.ASSIGN, 'Expecting =')
        self.expr()

    def lvalue(self):
        if(self.match(TokenType.ID)):
            self.advance()
            if(self.match(TokenType.LBRACKET)):
                self.advance()
                self.expr()
                self.eat(TokenType.RBRACKET, 'Expecting ]')
            # if(self.match(TokenType.DOT)):
            while(self.match(TokenType.DOT)):
                self.eat(TokenType.DOT, 'Expecting .')
                self.eat(TokenType.ID, 'Expecting ID')
                if(self.match(TokenType.LBRACKET)):
                    self.advance()
                    self.expr()
                    self.eat(TokenType.RBRACKET, 'Expecting ]')
        elif(self.match(TokenType.DOT) or self.match(TokenType.LBRACKET)):
            if(self.match(TokenType.LBRACKET)):
                self.advance()
                self.expr()
                self.eat(TokenType.RBRACKET, 'Expecting ]')
            # if(self.match(TokenType.DOT)):
            while(self.match(TokenType.DOT)):
                self.eat(TokenType.DOT, 'Expecting .')
                self.eat(TokenType.ID, 'Expecting ID')
                if(self.match(TokenType.LBRACKET)):
                    self.advance()
                    self.expr()
                    self.eat(TokenType.RBRACKET, 'Expecting ]')


    def if_stmt(self):
        if(self.match(TokenType.IF)):
            self.advance()
            # if(self.match(TokenType.LPAREN)):
            self.eat(TokenType.LPAREN, 'Expecting (')
            self.expr()
            self.eat(TokenType.RPAREN, 'Expecting )')
            self.eat(TokenType.LBRACE, 'Expecting {')
            while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN)
                or self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) 
                or self.match(TokenType.ASSIGN) or self.match(TokenType.ARRAY) or self.match(TokenType.ID)):
                    self.stmt()
            self.eat(TokenType.RBRACE, 'Expecting }')
            self.if_stmt_t()
            


    def if_stmt_t(self):
        if(self.match(TokenType.ELSEIF)):
            self.eat(TokenType.ELSEIF, 'Expecting ELSEIF')
            self.eat(TokenType.LPAREN, 'Expecting (')
            self.expr()
            self.eat(TokenType.RPAREN, 'Expecting )')
            self.eat(TokenType.LBRACE, 'Expecting {')
            while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN) or 
               self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or 
               self.match(TokenType.ARRAY) or self.match(TokenType.ASSIGN) or self.match(TokenType.ID)):
                    self.stmt()
            self.eat(TokenType.RBRACE, 'Expecting }')
            self.if_stmt_t()
        if(self.match(TokenType.ELSE)):
            self.eat(TokenType.ELSE, 'Expecting else')
            self.eat(TokenType.LBRACE, 'Expecting {')
            while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN) or 
               self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or 
               self.match(TokenType.ARRAY) or self.match(TokenType.ASSIGN) or self.match(TokenType.ID)):
                self.stmt()
            self.eat(TokenType.RBRACE, 'Expecting }')

    def while_stmt(self):
        if(self.match(TokenType.WHILE)):
            self.eat(TokenType.WHILE, 'Expecting while')
            self.eat(TokenType.LPAREN, 'Expecting (')
            self.expr()
            self.eat(TokenType.RPAREN, 'Expecting )') 
            self.eat(TokenType.LBRACE, 'Expecting {')
            while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN) or 
               self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or 
               self.match(TokenType.ARRAY) or self.match(TokenType.ASSIGN) or self.match(TokenType.ID)):
                self.stmt()
            self.eat(TokenType.RBRACE, 'Expecting }')          

    def for_stmt(self):
        if(self.match(TokenType.FOR)):
            self.eat(TokenType.FOR, 'Expecting for')
            self.eat(TokenType.LPAREN, 'Expecting (')
            self.vdecl_stmnt()
            self.eat(TokenType.SEMICOLON, 'Expecting ;')
            self.expr()
            self.eat(TokenType.SEMICOLON, 'Expecting ;')
            self.assign_stmt()
            self.eat(TokenType.RPAREN, 'Expecting )') 
            self.eat(TokenType.LBRACE, 'Expecting {')
            while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN) or 
               self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or 
               self.match(TokenType.ARRAY) or self.match(TokenType.ASSIGN) or self.match(TokenType.ID)):
                self.stmt()
            self.eat(TokenType.RBRACE, 'Expecting }')


    def call_expr(self):
        if(self.match(TokenType.LPAREN)):
            self.advance()
            if(self.match(TokenType.PLUS) or self.match(TokenType.MINUS) or self.match(TokenType.TIMES)
                or self.match(TokenType.DIVIDE) or self.match(TokenType.AND) or self.match(TokenType.OR)
                or self.match(TokenType.EQUAL) or self.match(TokenType.LESS) or self.match(TokenType.GREATER)
                or self.match(TokenType.LESS_EQ) or self.match(TokenType.GREATER_EQ) or self.match(TokenType.NOT_EQUAL)
                or self.match(TokenType.LPAREN) or self.match(TokenType.NOT) or self.match(TokenType.INT_VAL) or self.match(TokenType.DOUBLE_VAL) or self.match(TokenType.BOOL_VAL)
                or self.match(TokenType.STRING_VAL) or self.match(TokenType.NULL_VAL) or self.match(TokenType.ID) 
                or self.match(TokenType.NEW)):
                self.expr()
                while(self.match(TokenType.COMMA)):
                    self.advance()
                    self.expr()
            self.eat(TokenType.RPAREN, 'Expecting )')
            

    def return_stmt(self):
        if(self.match(TokenType.RETURN)):
            self.eat(TokenType.RETURN, 'Expecting return')
            self.expr()

    def expr(self):

        if(self.match(TokenType.INT_VAL) or self.match(TokenType.DOUBLE_VAL) or self.match(TokenType.BOOL_VAL)
             or self.match(TokenType.STRING_VAL) or self.match(TokenType.NULL_VAL) or self.match(TokenType.ID) 
             or self.match(TokenType.NEW)):
             self.rvalue()
        elif(self.match(TokenType.NOT)):
            self.advance()
            self.expr()
        elif(self.match(TokenType.LPAREN)):
            self.advance()
            self.expr()
            self.eat(TokenType.RPAREN, 'Expecting )')
        else:
            self.error('Improper expression syntax')
        
        if self.match_any([TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE
                        ,TokenType.AND, TokenType.OR, TokenType.EQUAL, TokenType.LESS, TokenType.GREATER
                        , TokenType.LESS_EQ, TokenType.GREATER_EQ, TokenType.NOT_EQUAL]):
                        self.bin_op()
                        self.expr()

    def bin_op(self):
        if(self.match(TokenType.PLUS)):
            self.advance()

        if(self.match(TokenType.MINUS)):
            self.advance()

        if(self.match(TokenType.TIMES)):
            self.advance()

        if(self.match(TokenType.DIVIDE)):
            self.advance()

        if(self.match(TokenType.AND)):
            self.advance()

        if(self.match(TokenType.OR)):
            self.advance()

        if(self.match(TokenType.EQUAL)):
            self.advance()

        if(self.match(TokenType.LESS)):
            self.advance()

        if(self.match(TokenType.GREATER)):
            self.advance()

        if(self.match(TokenType.LESS_EQ)):
            self.advance()

        if(self.match(TokenType.GREATER_EQ)):
            self.advance()
            
        if(self.match(TokenType.NOT_EQUAL)):
            self.advance()


    def rvalue(self):
        if(self.match(TokenType.NULL_VAL)):
            self.eat(TokenType.NULL_VAL, 'Expecting null')
        elif(self.match(TokenType.INT_VAL) or self.match(TokenType.DOUBLE_VAL) or self.match(TokenType.BOOL_VAL) or self.match(TokenType.STRING_VAL)):
            self.base_rvalue()
        elif(self.match(TokenType.NEW)):
            self.new_rvalue()
        elif(self.match(TokenType.ID)):
            self.eat(TokenType.ID, 'Expecting ID')
            if(self.match(TokenType.LBRACKET) or self.match(TokenType.DOT)):
                self.var_rvalue()
            if(self.match(TokenType.LPAREN)):
                self.call_expr()


    def new_rvalue(self):
        if(self.match(TokenType.NEW)):
            self.advance()

            if(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.STRING_TYPE)):
                self.base_type()
                if(self.match(TokenType.LBRACKET)):
                    self.eat(TokenType.LBRACKET, 'Expecting [')
                    if(self.match(TokenType.PLUS) or self.match(TokenType.MINUS) or self.match(TokenType.TIMES)
                        or self.match(TokenType.DIVIDE) or self.match(TokenType.AND) or self.match(TokenType.OR)
                        or self.match(TokenType.EQUAL) or self.match(TokenType.LESS) or self.match(TokenType.GREATER)
                        or self.match(TokenType.LESS_EQ) or self.match(TokenType.GREATER_EQ) or self.match(TokenType.NOT_EQUAL)
                        or self.match(TokenType.LPAREN) or self.match(TokenType.NOT) or self.match(TokenType.INT_VAL) or self.match(TokenType.DOUBLE_VAL) or self.match(TokenType.BOOL_VAL)
                        or self.match(TokenType.STRING_VAL) or self.match(TokenType.NULL_VAL) or self.match(TokenType.ID) 
                        or self.match(TokenType.NEW)):
                        self.expr()
                    self.eat(TokenType.RBRACKET, 'Expecting ]')                


            if(self.match(TokenType.ID)):
                self.advance()

                if(self.match(TokenType.LPAREN)):
                    self.advance()
                    if(self.match(TokenType.PLUS) or self.match(TokenType.MINUS) or self.match(TokenType.TIMES)
                        or self.match(TokenType.DIVIDE) or self.match(TokenType.AND) or self.match(TokenType.OR)
                        or self.match(TokenType.EQUAL) or self.match(TokenType.LESS) or self.match(TokenType.GREATER)
                        or self.match(TokenType.LESS_EQ) or self.match(TokenType.GREATER_EQ) or self.match(TokenType.NOT_EQUAL)
                        or self.match(TokenType.LPAREN) or self.match(TokenType.NOT) or self.match(TokenType.INT_VAL) or self.match(TokenType.DOUBLE_VAL) or self.match(TokenType.BOOL_VAL)
                        or self.match(TokenType.STRING_VAL) or self.match(TokenType.NULL_VAL) or self.match(TokenType.ID) 
                        or self.match(TokenType.NEW)):
                        self.expr()
                        while(self.match(TokenType.COMMA)):
                            self.advance()
                            self.expr()
                    self.eat(TokenType.RPAREN, 'Expecting )')
                    

                if(self.match(TokenType.LBRACKET)):
                    self.advance()
                    if(self.match(TokenType.PLUS) or self.match(TokenType.MINUS) or self.match(TokenType.TIMES)
                        or self.match(TokenType.DIVIDE) or self.match(TokenType.AND) or self.match(TokenType.OR)
                        or self.match(TokenType.EQUAL) or self.match(TokenType.LESS) or self.match(TokenType.GREATER)
                        or self.match(TokenType.LESS_EQ) or self.match(TokenType.GREATER_EQ) or self.match(TokenType.NOT_EQUAL)
                        or self.match(TokenType.LPAREN) or self.match(TokenType.NOT) or self.match(TokenType.INT_VAL) or self.match(TokenType.DOUBLE_VAL) or self.match(TokenType.BOOL_VAL)
                        or self.match(TokenType.STRING_VAL) or self.match(TokenType.NULL_VAL) or self.match(TokenType.ID) 
                        or self.match(TokenType.NEW)):
                        self.expr()
                    self.eat(TokenType.RBRACKET, 'Expecting ]')
            

    def base_rvalue(self):
        if(self.match(TokenType.INT_VAL)):
            self.advance()

        if(self.match(TokenType.DOUBLE_VAL)):
            self.advance()

        if(self.match(TokenType.BOOL_VAL)):
            self.advance()

        if(self.match(TokenType.STRING_VAL)):
            self.advance()

    def var_rvalue(self):
        if(self.match(TokenType.LBRACKET)):
            self.eat(TokenType.LBRACKET, 'Expecting {')
            self.expr()
            self.eat(TokenType.RBRACKET, 'Expecting }')
        while(self.match(TokenType.DOT)):
            self.advance()
            self.eat(TokenType.ID, 'Expecting ID')
            if(self.match(TokenType.LBRACKET)):
                self.advance()
                self.expr()
                self.eat(TokenType.RBRACKET, 'Expecting }')


