"""MyPL AST parser implementation.

NAME: Lauren Nguye
DATE: Spring 2024
CLASS: CPSC 326
"""

from mypl_error import *
from mypl_token import *
from mypl_lexer import *
from mypl_ast import *


class ASTParser:

    def __init__(self, lexer):
        """Create a MyPL syntax checker (parser). 
        
        Args:
            lexer -- The lexer to use in the parser.

        """
        self.lexer = lexer
        self.curr_token = None

        
    def parse(self):
        """Start the parser, returning a Program AST node."""
        program_node = Program([], [])
        self.advance()
        while not self.match(TokenType.EOS):
            if self.match(TokenType.STRUCT):
                self.struct_def(program_node)
            else:
                self.fun_def(program_node)
        self.eat(TokenType.EOS, 'expecting EOF')
        return program_node

        
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
        """Returns true if the current token is a binary operator."""
        ts = [TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE,
              TokenType.AND, TokenType.OR, TokenType.EQUAL, TokenType.LESS,
              TokenType.GREATER, TokenType.LESS_EQ, TokenType.GREATER_EQ,
              TokenType.NOT_EQUAL]
        return self.match_any(ts)




    #----------------------------------------------------------------------
    # Recursive descent functions
    #----------------------------------------------------------------------


    # TODO: Finish the recursive descent functions below. Note that
    # you should copy in your functions from HW-2 and then instrument
    # them to build the corresponding AST objects.

    def struct_def(self, program_node): 
        # Creating struct node from StructDef class
        struct_node = StructDef(None, None)
        self.eat(TokenType.STRUCT, 'Expecting STRUCT Token Type')

        # Setting the name of struct to the curr token(ID)
        struct_node.struct_name = self.curr_token
        self.eat(TokenType.ID, 'Expecting ID Token Type')
        self.eat(TokenType.LBRACE, 'Expecting { Token Type')

        # Setting local fields_node to return value of fields func(var_def list)
        fields_node = self.fields()

        # setting structs field param to the fields var_def_list
        struct_node.fields = fields_node
        self.eat(TokenType.RBRACE, 'Expecting } Token type')

        # appending built struct to the program node to build the AST
        program_node.struct_defs.append(struct_node)


        
    def fields(self):
        # Local list to hold var_def_nodes
        var_def_list = []

        # If there is no field(empty struct)return empty list
        if(self.match(TokenType.RBRACE)):
            return var_def_list

        # While curr token matches any data_type
        while(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.SEMICOLON) or self.match(TokenType.ID) or self.match(TokenType.ARRAY)):
            # creating var_def_node from the VarDef class
            var_def_node = VarDef(None, None)
            
            # setting var_def_nodes datatype param to return value of data_type(base type, ID, or array)
            var_def_node.data_type = self.data_type()

            # setting var_def_nodes variable name to the current token (ID)
            var_def_node.var_name = self.curr_token
            self.eat(TokenType.ID, 'Expecting ID TokenType')
            self.eat(TokenType.SEMICOLON, 'Expecting semicolon Token')

            # appending node to list
            var_def_list.append(var_def_node)

        return var_def_list
            
    def fun_def(self, program_node):
        # creating fun_def node from FunDef class
        fun_node = FunDef(None, None, None, None)

        # if the return type is a primitive type
        if(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.SEMICOLON) or self.match(TokenType.ID) or self.match(TokenType.ARRAY)):
            fun_node.return_type = self.data_type()
        
        # if the return type is a void type
        elif(self.match(TokenType.VOID_TYPE)):
            data_node = DataType(None, None)
            data_node.is_array = False
            data_node.type_name = self.curr_token
            fun_node.return_type = data_node
            self.eat(TokenType.VOID_TYPE, 'Expecting Void')

        # setting fun_nodes function name param to the current token(ID)
        fun_node.fun_name = self.curr_token

        self.eat(TokenType.ID, "Expecting ID Token type")
        self.eat(TokenType.LPAREN, 'Expecting ( Token type')

        # creating local variable to hold return of params(list of vardefs)
        params_node = self.params() 

        # setting fun_node params param to the list of var_defs
        fun_node.params = params_node

        self.eat(TokenType.RPAREN, 'Expecting ) Token type')
        self.eat(TokenType.LBRACE, "Expecting { Token Type")

        # creating local list to hold stmts
        stmt_list = []

        # while the token matches any of the tokens that begin stmts
        while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN)
                or self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) 
                or self.match(TokenType.SEMICOLON) or self.match(TokenType.ARRAY) or self.match(TokenType.ID) or self.match(TokenType.ASSIGN) or self.match(TokenType.TRY)):
                # append stmts from stmt() to the stmt_list
                stmt_list.append(self.stmt())

        self.eat(TokenType.RBRACE, 'Expecting } Token type')
        
        # set tje stmt param in fun_node to list of stmts
        fun_node.stmts = stmt_list

        # appending function node to the program node
        program_node.fun_defs.append(fun_node)

    def params(self):
        # local list to hold var def nodes
        params_list = []

        # if there is no params
        if(self.match(TokenType.RPAREN)):
            return params_list

        # while the token matches a data_type
        if(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.VOID_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.ARRAY) or self.match(TokenType.ID)):
            # creating node from VarDef class
            var_def_node = VarDef(None, None)

            # setting var_def_nodes data_type param to return of data_type(primitive, id, array)
            var_def_node.data_type = self.data_type()
            
            # setting var_def_nodes name param to the current token(ID)
            var_def_node.var_name = self.curr_token
            self.eat(TokenType.ID, 'Expected ID')

            # appending built up node to the local param list
            params_list.append(var_def_node)

            # if there is more than one parameter
            while(self.match(TokenType.COMMA)):
                 # creating node from VarDef class
                var_def_node = VarDef(None, None)
                self.eat(TokenType.COMMA, 'Expecting comma')

                # setting var_def_nodes data_type param to return of data_type(primitive, id, array)
                var_def_node.data_type = self.data_type()

                # setting var_def_nodes name param to the current token(ID)
                var_def_node.var_name = self.curr_token
                self.eat(TokenType.ID, 'Expecting ID')

                # appending built up node to the local param list
                params_list.append(var_def_node)

        # return list of var_defs
        return params_list


    def data_type(self):
        # creating node from DataType class
        data_type_node = DataType(None, None)

        # if the token matches the base type primitives
        if(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.STRING_TYPE)):
            # set type to return of base_type(int, double, bool, or string)
            data_type_node.type_name = self.base_type()

            # not an array
            data_type_node.is_array = False

        # if the token matches a ID like a struct
        elif(self.match(TokenType.ID)):
            # set type to the current token
            data_type_node.type_name = self.curr_token

            # not an array
            data_type_node.is_array = False
            self.eat(TokenType.ID, 'Expecting ID')

        # if the token is a array
        elif(self.match(TokenType.ARRAY)):
            # set flag
            data_type_node.is_array = True
            self.eat(TokenType.ARRAY, 'Expecting Array Value')

            # if it is a ID type
            if(self.match(TokenType.ID)):
                # set data type to current token(ID)
                data_type_node.type_name = self.curr_token
                self.eat(TokenType.ID, 'Expecting ID')

            # if not an ID, then it is primitive base type
            else:
                # set type to primitive
                data_type_node.type_name = self.base_type()

        # return node 
        return data_type_node
            
    
    def base_type(self):

        # if it matches int
        if(self.match(TokenType.INT_TYPE)):
            base_node = self.curr_token
            self.advance()
            return base_node
            
        # if it matches double
        if(self.match(TokenType.DOUBLE_TYPE)):
            base_node = self.curr_token
            self.advance()
            return base_node
        
        # if it matches bool
        if(self.match(TokenType.BOOL_TYPE)):
            base_node = self.curr_token
            self.advance()
            return base_node
            
        # if it matches string
        if(self.match(TokenType.STRING_TYPE)):
            base_node = self.curr_token
            self.advance()
            return base_node
        

    def stmt(self):
        
        # if is it is a try catch stmt
        if(self.match(TokenType.TRY)):
            try_node = self.try_stmt()
            return try_node

        # if it is a while stmt
        if(self.match(TokenType.WHILE)):
            # create local while node to hold return of while_stmt
            while_node = self.while_stmt()
            return while_node

        # if it is a if stmt
        if(self.match(TokenType.IF)):
            # create local if node to hold return of if stmt
            if_node = self.if_stmt()
            return if_node

        # if it is a for loop
        if(self.match(TokenType.FOR)):
            # create local for node to hold return of for_stmt
            for_node = self.for_stmt()
            return for_node


        # if it is a return stmt
        if(self.match(TokenType.RETURN)):
            # create local return node to hold return of return_stmt
            return_node = self.return_stmt()
            self.eat(TokenType.SEMICOLON, 'Expecting ;')
            return return_node

        # if it is a vdecl that matches dataypes that are not IDs
        if(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.SEMICOLON) or self.match(TokenType.ARRAY)):
            # create local var_decl_node to hold return of vdecl_stmnt
            var_decl_node = self.vdecl_stmnt()
            self.eat(TokenType.SEMICOLON, 'Expecting ;')
            return var_decl_node

        # if it matches ID, it is either a vdecl starting with an ID, a call to a function, or an assignment stmt
        if(self.match(TokenType.ID)):
            # before advancing save ID for call_func()
            call_func_node = self.curr_token

            # before advancing save ID for assign_stmt
            id_node_assign = self.curr_token

            # determine "datatype" in case it is a vdecl stmt
            id_node = self.data_type()

            # call_expr case
            if(self.match(TokenType.LPAREN)):
                # create local variable to hold call node returned, sending in saved func name
                call_expr_node = self.call_expr(call_func_node)
                self.eat(TokenType.SEMICOLON, 'Expecting ;')
                return call_expr_node

            # assign_stmt case
            elif(self.match(TokenType.LBRACKET) or self.match(TokenType.DOT) or self.match(TokenType.ASSIGN)):
                # create local variable to hold assignment stmt returned, sending in saved ID name
                assign_stmt_node = self.assign_stmt(id_node_assign)
                self.eat(TokenType.SEMICOLON, 'Expecting ;')
                return assign_stmt_node

            # vdecl case
            elif(self.match(TokenType.ID)):
                # create local variable to hold vdecl returned, sending in saved "datatype"
                var_decl_node = self.vdecl_stmnt_id(id_node)
                self.eat(TokenType.SEMICOLON, 'Expecting ;')
                return var_decl_node
        

    def vdecl_stmnt(self):
        # creating node from VarDecl class
        var_decl_node = VarDecl(None, None)

        # creating node from VarDef class
        var_def_node = VarDef(None, None)

        # looking for datatypes
        if(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.SEMICOLON) or self.match(TokenType.ARRAY)):
            # set type to return of base_type(int, double, bool, or string)
            var_def_node.data_type = self.data_type()

            # setting name of var_def to the current token(ID)
            var_def_node.var_name = self.curr_token
            self.eat(TokenType.ID, 'Expecting ID')

            # setting var_decls var_def param to built var_def_node
            var_decl_node.var_def = var_def_node

            # if there is an assignment(lhs)
            if(self.match(TokenType.ASSIGN)):
                self.advance()

                # create local node to hold return of expr()
                expr_node = self.expr()
                
                # setting var_decl_nodes expr param to built expr_node
                var_decl_node.expr = expr_node
        return var_decl_node
    
    def vdecl_stmnt_id(self, data_type_variable):
        # creating node from VarDecl class
        var_decl_node = VarDecl(None, None)

        # creating node from VarDef class
        var_def_node = VarDef(None, None)

        # setting var_def_nodes data_type to passed in saved ID val from stmt
        var_def_node.data_type = data_type_variable

        # setting name of var_def to the current token(ID)
        var_def_node.var_name = self.curr_token
        self.advance()

        # setting var_decls var_def param to built var_def_node
        var_decl_node.var_def = var_def_node

        # if there is an assignment(lhs)
        if(self.match(TokenType.ASSIGN)):
            self.advance()

            # create local node to hold return of expr()
            expr_node = self.expr()

            # setting var_decl_nodes expr param to built expr_node
            var_decl_node.expr = expr_node
        return var_decl_node

    def assign_stmt(self, id_before = None):
        # creating node from AssignStmt class
        assign_node = AssignStmt(None, None)

        # creating local node to hold return of lvalue, passing in saved ID from stmt
        l_node = self.lvalue(id_before)

        # setting assign_nodes lvalue param to the return of self.lvalue
        assign_node.lvalue = l_node
        self.eat(TokenType.ASSIGN, 'Expecting =')

        # local variable to hold the rhs of the assignment stmt
        expr_node = self.expr()

        # setting assign_nodes expr param to built expr node
        assign_node.expr = expr_node
        return assign_node

    def lvalue(self, id_before = None):
        # looking for the correct start to the lvalues(dots, left bracket, or a assign)
        if(self.match(TokenType.ASSIGN) or self.match(TokenType.DOT) or self.match(TokenType.LBRACKET)):
            # creating node from VarRef class
            var_ref_node = VarRef(None, None) 

            # creating list to hold var_ref nodes
            var_ref_list = []

            # using saved ID passed by assign_stmt to set the var_name param in var_ref
            var_ref_node.var_name = id_before

            # array case
            if(self.match(TokenType.LBRACKET)):
                self.advance()

                # create local node to hold return of expr()
                expr_node = self.expr()

                # set array_expr param to expr_node
                var_ref_node.array_expr = expr_node
                self.eat(TokenType.RBRACKET, 'Expecting ]')

            # appending built node to var_ref_list
            var_ref_list.append(var_ref_node)

            # struct case
            while(self.match(TokenType.DOT)):
                # making a new node from VarRef
                var_ref_node = VarRef(None, None) 
                self.eat(TokenType.DOT, 'Expecting .')

                # setting var_name param to curr token(ID)
                var_ref_node.var_name = self.curr_token
                self.eat(TokenType.ID, 'Expecting ID')

                # array case
                if(self.match(TokenType.LBRACKET)):
                    self.eat(TokenType.LBRACKET, 'Expected [')

                    # create local node to hold return of expr()
                    expr_node = self.expr()

                    # set array_expr param to built expr node
                    var_ref_node.array_expr = expr_node
                    self.eat(TokenType.RBRACKET, 'Expecting ]')

                # append node to list
                var_ref_list.append(var_ref_node)
            
            # setting node to return to the built list
            var_ref_node = var_ref_list
            return var_ref_list
        # else:
        #     self.error("Missing assignment operator")


    def if_stmt(self):
        # looking for if stmt token
        if(self.match(TokenType.IF)):
            # creating node from IfStmt class
            if_node = IfStmt(None, None, None)

            # creating node from BasicIf class
            basic_if_node = BasicIf(None, None)
            self.advance()
            self.eat(TokenType.LPAREN, 'Expecting (')

            # create local node to hold return of expr()
            expr_node = self.expr()

            # setting basic if condition param to expr_node
            basic_if_node.condition = expr_node
            self.eat(TokenType.RPAREN, 'Expecting )')
            self.eat(TokenType.LBRACE, 'Expecting {')

            # creating list to hold stmt's
            stmt_list = []

            # checking for stmt reserved words / initializers
            while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN)
                or self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) 
                or self.match(TokenType.ASSIGN) or self.match(TokenType.ARRAY) or self.match(TokenType.ID)) or self.match(TokenType.TRY):
                    # creating local node to hold return from stmt()
                    stmt_node = self.stmt()

                    # appending built node to the list
                    stmt_list.append(stmt_node)

            # setting stmts param in basic if to the built list
            basic_if_node.stmts = stmt_list
            self.eat(TokenType.RBRACE, 'Expecting }')

            # setting intial if stmt to the built basic_if_node built abve
            if_node.if_part = basic_if_node

            # creating list to hold else ifs and else stmts
            else_if_list = []

            # creting local variable to hold return of if_stmt_t(elifs and else), sending in intialized list
            elif_node = self.if_stmt_t(else_if_list)

            # creating list to hold elses
            else_node = []

            # creating list to hold all elifs
            end_elif_list = []

            # iterating through the list
            for else_if in elif_node:
                # if there is no condition --> it is the else stmt
                if(else_if.condition == None):
                    else_node = else_if.stmts
                
                # otherwise it is a elif
                else:
                    end_elif_list.append(else_if)

            # if there is something in the else list --> elses in code
            if not else_node == None:
                # set else_ifs to the final elif list
                if_node.else_ifs = end_elif_list
                # set else to else_node
                if_node.else_stmts = else_node

                # otherwise there is only elifs
            else:
                if_node.else_ifs = end_elif_list 
            return if_node

    def if_stmt_t(self, else_if_list=None):
        # while the token matches elseif or else
        if(self.match(TokenType.ELSEIF) or self.match(TokenType.ELSE)):
            # while loop to iterate of elseifs
            while(self.match(TokenType.ELSEIF)):
                # creating node from the BasicIf class
                if_basic_node = BasicIf(None, None)
                self.eat(TokenType.ELSEIF, 'Expecting ELSEIF')
                self.eat(TokenType.LPAREN, 'Expecting (')

                # creating node to hold return of expr(elif condition)
                expr_node = self.expr()

                # setting the condition of the if node to the found expression
                if_basic_node.condition = expr_node
                self.eat(TokenType.RPAREN, 'Expecting )')
                self.eat(TokenType.LBRACE, 'Expecting {')

                # local list to hold stmt's
                stmt_list = []

                # checking for stmt reserved words / initializers
                while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN) or 
                self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or 
                self.match(TokenType.ARRAY) or self.match(TokenType.ASSIGN) or self.match(TokenType.ID)) or self.match(TokenType.TRY):
                        # creating local node to hold return of stmt
                        stmt_node = self.stmt()

                        # appending built node to the stmt list
                        stmt_list.append(stmt_node)
                self.eat(TokenType.RBRACE, 'Expecting }')

                # setting the stmt param to the list
                if_basic_node.stmts = stmt_list

                # appending the node to the passed in list
                else_if_list.append(if_basic_node)
            
            if(self.match(TokenType.ELSE)):
                # creating node form the BasicIf
                if_basic_node = BasicIf(None, None)
                self.eat(TokenType.ELSE, 'Expecting else')
                self.eat(TokenType.LBRACE, 'Expecting {')

                # list to hold stmts
                stmt_list = []

                # checking for stmt reserved words / initializers
                while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN) or 
                self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or 
                self.match(TokenType.ARRAY) or self.match(TokenType.ASSIGN) or self.match(TokenType.ID)) or self.match(TokenType.TRY):
                    # creating local node to hold return of stmt
                    stmt_node = self.stmt()

                    # appending built node to the stmt list
                    stmt_list.append(stmt_node)
                self.eat(TokenType.RBRACE, 'Expecting }')

                # setting the stmt param to the list
                if_basic_node.stmts = stmt_list

                # appending the node to the passed in list
                else_if_list.append(if_basic_node)

            return else_if_list

        # no elses or elifs
        else:
            return else_if_list
        
    def try_stmt(self):
        try_node = TryCatchStmt(None, None)
        self.eat(TokenType.TRY, "Expecting Try")
        self.eat(TokenType.LBRACE, "Expecting {")
        # list to hold stmt nodes
        stmt_list = []

        # checking for tokens starting with stmts
        while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN)
                or self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) 
                or self.match(TokenType.SEMICOLON) or self.match(TokenType.ARRAY) or self.match(TokenType.ID) or self.match(TokenType.ASSIGN) or self.match(TokenType.TRY)):
                # adding node to list
                stmt_node = self.stmt()
                stmt_list.append(stmt_node)

        # setting stmts param to built list
        try_node.try_part = stmt_list
        self.eat(TokenType.RBRACE, "Expecting }")

        self.eat(TokenType.CATCH, "Expecting catch block")

        self.eat(TokenType.LBRACE, "Expecting {")
        
        stmt_list = []
        # checking for tokens starting with stmts
        while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN)
                or self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) 
                or self.match(TokenType.SEMICOLON) or self.match(TokenType.ARRAY) or self.match(TokenType.ID) or self.match(TokenType.ASSIGN)):
                
                # calling stmt
                stmt_node = self.stmt()

                # adding node to list
                stmt_list.append(stmt_node)

            # setting stmts param to built list
        try_node.catch_parts = stmt_list
        self.eat(TokenType.RBRACE, "Expecting }")

        return try_node
        

    def while_stmt(self):
        # creating node from WhileStmt Class
        while_node = WhileStmt(None, None)

        # matching while condition
        if(self.match(TokenType.WHILE)):
            self.eat(TokenType.WHILE, 'Expecting while')
            self.eat(TokenType.LPAREN, 'Expecting (')

            # set local node to return of expr(expressions)
            expr_node = self.expr()

            # setting while condition param to found expr
            while_node.condition = expr_node
            self.eat(TokenType.RPAREN, 'Expecting )') 
            self.eat(TokenType.LBRACE, 'Expecting {')

            # list to hold stmt nodes
            stmt_list = []

            # checking for tokens starting with stmts
            while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN)
                    or self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) 
                    or self.match(TokenType.SEMICOLON) or self.match(TokenType.ARRAY) or self.match(TokenType.ID) or self.match(TokenType.ASSIGN) or self.match(TokenType.TRY)):
                    # adding node to list
                    stmt_list.append(self.stmt())

            # setting stmts param to built list
            while_node.stmts = stmt_list
            self.eat(TokenType.RBRACE, 'Expecting }')
        return while_node       

    def for_stmt(self):
        # creating node from the ForStmt class
        for_node = ForStmt(None, None, None, None)

        # matching for conditon
        if(self.match(TokenType.FOR)):
            self.eat(TokenType.FOR, 'Expecting for')
            self.eat(TokenType.LPAREN, 'Expecting (')
            
            # setting local node to return of vdecl stmt
            v_decl_node = None
            if(self.match(TokenType.ID)):
                v_decl_node = self.vdecl_stmnt_id()
            else:
                v_decl_node = self.vdecl_stmnt()

            # setting var_decl node to the for param
            for_node.var_decl = v_decl_node

            self.eat(TokenType.SEMICOLON, 'Expecting ;')

            # local node to hold found expression from expr()
            expr_node = self.expr()

            # setting condition to found expression
            for_node.condition = expr_node

            self.eat(TokenType.SEMICOLON, 'Expecting ;')

            id_node = self.curr_token
            self.advance()

            # setting local node to assignment statement found
            assign_node = self.assign_stmt(id_node)

            # setting assign param in for to found assignment
            for_node.assign_stmt = assign_node
            self.eat(TokenType.RPAREN, 'Expecting )') 
            self.eat(TokenType.LBRACE, 'Expecting {')

            # list to hold stmt nodes
            stmt_list = []
            while(self.match(TokenType.WHILE) or self.match(TokenType.IF) or self.match(TokenType.FOR) or self.match(TokenType.RETURN) or 
               self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.STRING_TYPE) or self.match(TokenType.BOOL_TYPE) or 
               self.match(TokenType.ARRAY) or self.match(TokenType.ASSIGN) or self.match(TokenType.ID) or self.match(TokenType.TRY)):
                # setting node to found stmt
                stmt_node = self.stmt()

                # adding node to list
                stmt_list.append(stmt_node)

            # setting stmt param to stmt list built
            for_node.stmts = stmt_list
            self.eat(TokenType.RBRACE, 'Expecting }')

            return for_node


    def call_expr(self, id_node):
        # creating node from the CallExpr class
        call_expr_node = CallExpr(None, None)

        # using passed in saved ID, set fun_name param to it
        call_expr_node.fun_name = id_node

        # looking for start to call
        if(self.match(TokenType.LPAREN)):
            self.advance()

            # list to hold expr nodes
            expr_list = []
            if(self.match(TokenType.PLUS) or self.match(TokenType.MINUS) or self.match(TokenType.TIMES)
                or self.match(TokenType.DIVIDE) or self.match(TokenType.AND) or self.match(TokenType.OR)
                or self.match(TokenType.EQUAL) or self.match(TokenType.LESS) or self.match(TokenType.GREATER)
                or self.match(TokenType.LESS_EQ) or self.match(TokenType.GREATER_EQ) or self.match(TokenType.NOT_EQUAL)
                or self.match(TokenType.LPAREN) or self.match(TokenType.NOT) or self.match(TokenType.INT_VAL) or self.match(TokenType.DOUBLE_VAL) or self.match(TokenType.BOOL_VAL)
                or self.match(TokenType.STRING_VAL) or self.match(TokenType.NULL_VAL) or self.match(TokenType.ID) 
                or self.match(TokenType.NEW)):
                # setting local nodes to expression found
                expr_node = self.expr()

                # appending node to list
                expr_list.append(expr_node)

                # if there is multiple params
                while(self.match(TokenType.COMMA)):
                    self.advance()

                    # finding next param
                    expr_node = self.expr()
                    expr_list.append(expr_node)

            # setting built expr list to args param
            call_expr_node.args = expr_list
            self.eat(TokenType.RPAREN, 'Expecting )')
        return call_expr_node
            

    def return_stmt(self):
        # creating node from ReturnStmt class
        return_node = ReturnStmt(None)

        # looking for condition
        if(self.match(TokenType.RETURN)):
            self.eat(TokenType.RETURN, 'Expecting return')

            # using local expr_node to found expression
            expr_node = self.expr()

        # setting expr param to found expression
        return_node.expr = expr_node
        return return_node


    def expr(self, expr_node = None):
        # creating node from the Expr class
        expr_node = Expr(None, None, None, None)

        # looking for basic r -values (simple terms)
        if(self.match(TokenType.INT_VAL) or self.match(TokenType.DOUBLE_VAL) or self.match(TokenType.BOOL_VAL)
             or self.match(TokenType.STRING_VAL) or self.match(TokenType.NULL_VAL) or self.match(TokenType.ID) 
             or self.match(TokenType.NEW)):
            if(expr_node.not_op != True):
                expr_node.not_op = False

            # setting r_value_node to found rhs
            r_value_node = self.rvalue()

            # setting the first of the expr_node(ExprTerm) to found r -value
            expr_node.first = r_value_node

        # finding NOT expr case
        elif(self.match(TokenType.NOT)):
            self.advance()

            # finding the expression after the NOT
            expr_node = self.expr()

            # setting not_op to true since it has a NOT
            expr_node.not_op = True

        # looking for complex expressions
        elif(self.match(TokenType.LPAREN)):
            # creating new expr node
            expr_node = Expr(False, None, None, None)

            # creating node from ComplexTerm class
            complex_term_node = ComplexTerm(None)
            self.advance()

            # setting expr param in complex node to the found expr
            complex_term_node.expr = self.expr()

            # setting the first param(ExprTerm) to the complex node
            expr_node.first = complex_term_node
            self.eat(TokenType.RPAREN, 'Expecting )')
        else:
            self.error('Improper expression syntax')
        
        # looking for binary operators
        if self.match_any([TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE
                        ,TokenType.AND, TokenType.OR, TokenType.EQUAL, TokenType.LESS, TokenType.GREATER
                        , TokenType.LESS_EQ, TokenType.GREATER_EQ, TokenType.NOT_EQUAL]):
                        # determining bin operator to expr param
                        expr_node.op = self.bin_op()

                        # finding the rest of the expression
                        expr_results = self.expr()

                        # setting the results of expr param to the rest of the expr
                        expr_node.rest = expr_results
                        
                        return expr_node
        return expr_node

    def bin_op(self):
        if(self.match(TokenType.PLUS)):
            operator_node = self.curr_token
            self.advance()
            return operator_node

        if(self.match(TokenType.MINUS)):
            operator_node = self.curr_token
            self.advance()
            return operator_node

        if(self.match(TokenType.TIMES)):
            operator_node = self.curr_token
            self.advance()
            return operator_node

        if(self.match(TokenType.DIVIDE)):
            operator_node = self.curr_token
            self.advance()
            return operator_node

        if(self.match(TokenType.AND)):
            operator_node = self.curr_token
            self.advance()
            return operator_node

        if(self.match(TokenType.OR)):
            operator_node = self.curr_token
            self.advance()
            return operator_node

        if(self.match(TokenType.EQUAL)):
            operator_node = self.curr_token
            self.advance()
            return operator_node

        if(self.match(TokenType.LESS)):
            operator_node = self.curr_token
            self.advance()
            return operator_node

        if(self.match(TokenType.GREATER)):
            operator_node = self.curr_token
            self.advance()
            return operator_node

        if(self.match(TokenType.LESS_EQ)):
            operator_node = self.curr_token
            self.advance()
            return operator_node

        if(self.match(TokenType.GREATER_EQ)):
            operator_node = self.curr_token
            self.advance()
            return operator_node
            
        if(self.match(TokenType.NOT_EQUAL)):
            operator_node = self.curr_token
            self.advance()
            return operator_node


    def rvalue(self):
        # looking for the NULL case
        if(self.match(TokenType.NULL_VAL)):
            # creating node from SimpleTerm class
            simple_node = SimpleTerm(None) 

            # creating node from the SimpleRValue class
            simple_r_node = SimpleRValue(None)

            # setting the value of the node to the current token
            simple_r_node.value = self.curr_token
            self.advance() 

            # attaching the rval to the original node
            simple_node.rvalue = simple_r_node
            return simple_node

        # base type case
        elif(self.match(TokenType.INT_VAL) or self.match(TokenType.DOUBLE_VAL) or self.match(TokenType.BOOL_VAL) or self.match(TokenType.STRING_VAL)):
            # create simple node from SimpleTerm class
            simple_node = SimpleTerm(None) 

            # finding base value and setting the rvalue param
            simple_node.rvalue = self.base_rvalue()
            return simple_node

        # new r val case
        elif(self.match(TokenType.NEW)):
            # creating node from SimpleTerm class
            simple_node = SimpleTerm(None) 

            # setting the node to the return of new_rvalue()
            new_r_val_node = self.new_rvalue()

            # attaching the rval to the original node
            simple_node.rvalue = new_r_val_node
            return simple_node

        # call expr or var reference case 
        elif(self.match(TokenType.ID)):

            # saving ID to send to var ref and call expr
            id_node = self.curr_token
            self.eat(TokenType.ID, 'Expecting ID')

            # call expr case
            if(self.match(TokenType.LPAREN)):

                # creating node from call expr and sending in saved ID
                call_expr_node = self.call_expr(id_node)
                return call_expr_node

            # var ref case
            else:
                # creating node from SimpleTerm class
                simple_node = SimpleTerm(None) 

                # setting node to the return of var_rvalue and sending in saved ID
                var_rvalue_node = self.var_rvalue(id_node)
                simple_node.rvalue = var_rvalue_node
                return simple_node


    def new_rvalue(self):
        # checking condition
        if(self.match(TokenType.VOID_TYPE)):
            new_r_val_node = NewRValue(None, None, None)
            new_r_val_node.type_name = self.curr_token
            self.advance()

        if(self.match(TokenType.NEW)):
            self.advance()

            # looking for base types
            if(self.match(TokenType.INT_TYPE) or self.match(TokenType.DOUBLE_TYPE) or self.match(TokenType.BOOL_TYPE) or self.match(TokenType.STRING_TYPE)):

                # creating new node from NewRValue class
                new_r_val_node = NewRValue(None, None, None)

                # setting the type name to a found base type
                new_r_val_node.type_name = self.base_type()

                # array case
                if(self.match(TokenType.LBRACKET)):
                    self.eat(TokenType.LBRACKET, 'Expecting [')

                    # looking for any expr token
                    if(self.match(TokenType.PLUS) or self.match(TokenType.MINUS) or self.match(TokenType.TIMES)
                        or self.match(TokenType.DIVIDE) or self.match(TokenType.AND) or self.match(TokenType.OR)
                        or self.match(TokenType.EQUAL) or self.match(TokenType.LESS) or self.match(TokenType.GREATER)
                        or self.match(TokenType.LESS_EQ) or self.match(TokenType.GREATER_EQ) or self.match(TokenType.NOT_EQUAL)
                        or self.match(TokenType.LPAREN) or self.match(TokenType.NOT) or self.match(TokenType.INT_VAL) or self.match(TokenType.DOUBLE_VAL) or self.match(TokenType.BOOL_VAL)
                        or self.match(TokenType.STRING_VAL) or self.match(TokenType.NULL_VAL) or self.match(TokenType.ID) 
                        or self.match(TokenType.NEW)):

                        # setting array node to expr found
                        array_expr_node = self.expr()

                    # setting array_expr param in new_r_val_node to found array expr
                    new_r_val_node.array_expr = array_expr_node 
                    self.eat(TokenType.RBRACKET, 'Expecting ]')    
                return new_r_val_node         

            # other case if there is no base type
            if(self.match(TokenType.ID)):
                # creating new node from NewRValue class
                new_r_val_node = NewRValue(None, None, None)

                # setting the type name to the curr token(ID)
                new_r_val_node.type_name = self.curr_token
                self.advance()

                # struct case
                if(self.match(TokenType.LPAREN)):
                    self.advance()

                    # creating list to hold parameters found(expr nodes)
                    struct_param_list = []

                    # checking for expr intializers
                    if(self.match(TokenType.PLUS) or self.match(TokenType.MINUS) or self.match(TokenType.TIMES)
                        or self.match(TokenType.DIVIDE) or self.match(TokenType.AND) or self.match(TokenType.OR)
                        or self.match(TokenType.EQUAL) or self.match(TokenType.LESS) or self.match(TokenType.GREATER)
                        or self.match(TokenType.LESS_EQ) or self.match(TokenType.GREATER_EQ) or self.match(TokenType.NOT_EQUAL)
                        or self.match(TokenType.LPAREN) or self.match(TokenType.NOT) or self.match(TokenType.INT_VAL) or self.match(TokenType.DOUBLE_VAL) or self.match(TokenType.BOOL_VAL)
                        or self.match(TokenType.STRING_VAL) or self.match(TokenType.NULL_VAL) or self.match(TokenType.ID) 
                        or self.match(TokenType.NEW)):
                        # setting node to found struct expr
                        struct_expr_node = self.expr()
                        
                        # appending node to list
                        struct_param_list.append(struct_expr_node)

                        # if there is more than one params
                        while(self.match(TokenType.COMMA)):
                            self.advance()

                            # setting node to found struct expr
                            struct_expr_node = self.expr()

                            # appending node to list
                            struct_param_list.append(struct_expr_node)

                    # setting params param to built list 
                    new_r_val_node.struct_params = struct_param_list
                    self.eat(TokenType.RPAREN, 'Expecting )')
                    return new_r_val_node
                    
                # array case
                if(self.match(TokenType.LBRACKET)):
                    self.advance()

                    # looking for any expr token
                    if(self.match(TokenType.PLUS) or self.match(TokenType.MINUS) or self.match(TokenType.TIMES)
                        or self.match(TokenType.DIVIDE) or self.match(TokenType.AND) or self.match(TokenType.OR)
                        or self.match(TokenType.EQUAL) or self.match(TokenType.LESS) or self.match(TokenType.GREATER)
                        or self.match(TokenType.LESS_EQ) or self.match(TokenType.GREATER_EQ) or self.match(TokenType.NOT_EQUAL)
                        or self.match(TokenType.LPAREN) or self.match(TokenType.NOT) or self.match(TokenType.INT_VAL) or self.match(TokenType.DOUBLE_VAL) or self.match(TokenType.BOOL_VAL)
                        or self.match(TokenType.STRING_VAL) or self.match(TokenType.NULL_VAL) or self.match(TokenType.ID) 
                        or self.match(TokenType.NEW)):
                        # setting array node to expr found
                        array_expr_node = self.expr()

                    # setting array_expr param in new_r_val_node to found array expr
                    new_r_val_node.array_expr = array_expr_node
                    self.eat(TokenType.RBRACKET, 'Expecting ]')
                    return new_r_val_node
            

    def base_rvalue(self):
        simple_r_node = SimpleRValue(None)
        if(self.match(TokenType.INT_VAL)):
            simple_r_node.value = self.curr_token
            self.advance()
            return simple_r_node

        if(self.match(TokenType.DOUBLE_VAL)):
            simple_r_node.value = self.curr_token
            self.advance()
            return simple_r_node

        if(self.match(TokenType.BOOL_VAL)):
            simple_r_node.value = self.curr_token
            self.advance()
            return simple_r_node

        if(self.match(TokenType.STRING_VAL)):
            simple_r_node.value = self.curr_token
            self.advance()
            return simple_r_node

    def var_rvalue(self, id_node = None):
        # creating list to hold var_refs
        var_ref_list = []

        # creating node from VarRef class
        var_ref_node = VarRef(None, None)

        # creating node from VarRValue class
        var_r_val_node = VarRValue(None)

        # setting var_name param to saved ID
        var_ref_node.var_name = id_node
        
        # array case
        if(self.match(TokenType.LBRACKET)):
            self.eat(TokenType.LBRACKET, 'Expecting [')

            # setting expr_node to returned expr
            expr_node = self.expr()

            # setting expr param in var ref node
            var_ref_node.array_expr = expr_node
            self.eat(TokenType.RBRACKET, 'Expecting ]')
        
        # appending node to list
        var_ref_list.append(var_ref_node)

        # struct case
        while(self.match(TokenType.DOT)):
            # creating node from VarRef class
            var_ref_node = VarRef(None, None)
            self.advance()

            # setting variable name to current token(ID)
            var_ref_node.var_name = self.curr_token
            self.eat(TokenType.ID, 'Expecting ID')

            # array case
            if(self.match(TokenType.LBRACKET)):
                self.advance()

                # setting expr_node to returned expr
                expr_node = self.expr()

                # setting expr param in var ref node
                var_ref_node.array_expr = expr_node
                self.eat(TokenType.RBRACKET, 'Expecting ]')

            # appending node to list
            var_ref_list.append(var_ref_node)

        # setting path param to var ref list
        var_r_val_node.path = var_ref_list
        return var_r_val_node




    
                
            
