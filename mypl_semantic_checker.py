"""Semantic Checker Visitor for semantically analyzing a MyPL program.

NAME: Lauren Nguyen
DATE: Spring 2024
CLASS: CPSC 326

"""

from dataclasses import dataclass
from mypl_error import *
from mypl_token import Token, TokenType
from mypl_ast import *
from mypl_symbol_table import SymbolTable


BASE_TYPES = ['int', 'double', 'bool', 'string']
BUILT_INS = ['print', 'input', 'itos', 'itod', 'dtos', 'dtoi', 'stoi', 'stod',
             'length', 'get']
CONDITIONAL_NON_BOOL_RHS_LHS = ['<', '>', '<=', '>=', '==', '!=']
CONDITIONAL_BOOL_RHS_LHS = ['<', '>', '<=', '>=']
OPERATORS_NO_PLUS = ['-', '*', '/']
COMPAIRSON_OPERATORS = ['and', 'or']

class SemanticChecker(Visitor):
    """Visitor implementation to semantically check MyPL programs."""

    def __init__(self):
        self.structs = {}
        self.functions = {}
        self.symbol_table = SymbolTable()
        self.curr_type = None


    # Helper Functions

    def error(self, msg, token):
        """Create and raise a Static Error."""
        if token is None:
            raise StaticError(msg)
        else:
            m = f'{msg} near line {token.line}, column {token.column}'
            raise StaticError(m)


    def get_field_type(self, struct_def, field_name):
        """Returns the DataType for the given field name of the struct
        definition.

        Args:
            struct_def: The StructDef object 
            field_name: The name of the field

        Returns: The corresponding DataType or None if the field name
        is not in the struct_def.

        """
        for var_def in struct_def.fields:
            if var_def.var_name.lexeme == field_name:
                return var_def.data_type
        return None

        
    # Visitor Functions
    
    def visit_program(self, program):
        # check and record struct defs
        for struct in program.struct_defs:
            struct_name = struct.struct_name.lexeme
            if struct_name in self.structs:
                self.error(f'duplicate {struct_name} definition', struct.struct_name)
            self.structs[struct_name] = struct
        # check and record function defs
        for fun in program.fun_defs:
            fun_name = fun.fun_name.lexeme
            if fun_name in self.functions: 
                self.error(f'duplicate {fun_name} definition', fun.fun_name)
            if fun_name in BUILT_INS:
                self.error(f'redefining built-in function', fun.fun_name)
            if fun_name == 'main' and fun.return_type.type_name.lexeme != 'void':
                self.error('main without void type', fun.return_type.type_name)
            if fun_name == 'main' and fun.params: 
                self.error('main function with parameters', fun.fun_name)
            self.functions[fun_name] = fun
        # check main function
        if 'main' not in self.functions:
            self.error('missing main function', None)
        # check each struct
        for struct in self.structs.values():
            struct.accept(self)
        # check each function
        for fun in self.functions.values():
            fun.accept(self)
        
        
    def visit_struct_def(self, struct_def):

        self.symbol_table.push_environment()

        # checking that the struct exists
        if struct_def.struct_name is None:
            self.error("Structs must have a name!", None)

        # while there is fields, enter if
        if struct_def.fields != []:

            # loop through fields checking for invalid types
            for var_def in struct_def.fields:
                field_type_name = var_def.data_type.type_name.lexeme
                if field_type_name not in BASE_TYPES and field_type_name not in self.structs:
                    self.error(f'undefined field type "{field_type_name}"', var_def.data_type.type_name)
                    
            # Initialize a set to store field names
            field_names = set()
            
            # Check each field's name
            for var_def in struct_def.fields:
                field_name = var_def.var_name.lexeme

                # if the field name is already declared, error
                if field_name in field_names:
                    self.error(f'duplicate field name "{field_name}" in struct "{struct_def.struct_name.lexeme}"', var_def.var_name)
                else:
                    field_names.add(field_name)
                # add field to symbol table
                self.symbol_table.add(field_name, var_def.data_type)
        self.symbol_table.pop_environment()
        

    def visit_fun_def(self, fun_def):
        self.symbol_table.push_environment()

        # Initialize a set to store parameter names if there are any
        if fun_def.params:
            param_names = set()
            
            # looping through parameters to check duplicates
            for param in fun_def.params:
                param_name = param.var_name.lexeme

                # if param name is already declared, error
                if param_name in param_names:
                    self.error(f'duplicate parameter definition: {param_name}', param.var_name)
                else:
                    param_names.add(param_name)
                # Add parameters to the symbol table
                self.symbol_table.add(param_name, param.data_type)

        # checking return type is valid
        if fun_def.return_type is not None:
            return_type_name = fun_def.return_type.type_name.lexeme
            if return_type_name not in BASE_TYPES and return_type_name not in self.structs and return_type_name != 'void':
                self.error(f'Unsupported return type "{return_type_name}"', fun_def.return_type.type_name)

        # adding return type to symbol table
        self.symbol_table.add('return', fun_def.return_type)
        
        # Visit each statement in the function body
        self.symbol_table.push_environment()
        for stmt in fun_def.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()
        

        self.symbol_table.pop_environment()


        
    def visit_return_stmt(self, return_stmt):
        # Retrieve the return type from the symbol table
        return_type = self.symbol_table.get('return')

        # Visit the expression attached to the return statement
        return_stmt.expr.accept(self)

        # Check if the type of the returned expression is compatible with the return type
        if return_type.is_array:
            if return_type.type_name.token_type == TokenType.VOID_TYPE:
                self.error(f'Return type mismatch: Expected "{return_type.type_name.lexeme}, but got "{self.curr_type.type_name.lexeme}"', self.curr_type.type_name)
            if return_type.type_name.token_type != self.curr_type.type_name.token_type:
                self.error(f'Return type mismatch: Expected "{return_type.type_name.lexeme}, but got "{self.curr_type.type_name.lexeme}"', self.curr_type.type_name)
      
        # if the type is not a array
        else:
            # if return type is not void check for compatible types
            if return_type.type_name.lexeme != 'void':
                if return_type.type_name.lexeme != self.curr_type.type_name.lexeme:
                    if(self.curr_type.type_name.lexeme != 'void'):
                        self.error(f'Return type mismatch: Expected "{return_type.type_name.lexeme}" or "null", but got "{self.curr_type.type_name.lexeme}"', self.curr_type.type_name)
            # ensureing that void has no return stmt
            if return_type.type_name.lexeme == 'void' and self.curr_type.type_name.lexeme != 'void':
                self.error(f'Return type mismatch: Void return type, no Return expected.', self.curr_type.type_name)

            
    def visit_var_decl(self, var_decl):
        # storing current variable name
        var_name = var_decl.var_def.var_name.lexeme

        # storing the declared data type
        declared_type = var_decl.var_def.data_type

        # checking intitalized variables
        if var_decl.expr != None:

            # if it is an array
            if var_decl.var_def.data_type.is_array:

                # accepting expression
                var_decl.expr.accept(self)

                # Check if variable name exists in the current function symbol table
                if self.symbol_table.exists_in_curr_env(var_name):
                    self.error(f'duplicate variable definition: {var_name}', var_decl.var_def.var_name)

                # checking compatible data types
                if self.curr_type.is_array == False and self.curr_type.type_name.token_type != TokenType.VOID_TYPE:
                    self.error("Incorrect array syntax", var_decl.var_def.var_name)

                # checking more compatuble types
                if declared_type.type_name.token_type != self.curr_type.type_name.token_type and self.curr_type.type_name.token_type != TokenType.VOID_TYPE:
                    self.error(f'Mismatched typing: {var_name}', var_decl.var_def.var_name)
                
                # adding the vairable to symbol table
                self.symbol_table.add(var_name, var_decl.var_def.data_type)

            else:
                # get expression
                var_decl.expr.accept(self)
                # Check if variable name exists in the current function symbol table
                if self.symbol_table.exists_in_curr_env(var_name):
                    self.error(f'duplicate variable definition: {var_name}', var_decl.var_def.var_name)

                # check if type is in structs
                if declared_type.type_name.lexeme in self.structs:
                    assigned_type = self.structs[declared_type.type_name.lexeme]
                else:
                    # Check if the assigned type matches the declared type
                    if declared_type.type_name.token_type != self.curr_type.type_name.token_type and self.curr_type.type_name.token_type != TokenType.VOID_TYPE:
                        self.error(f'Type mismatch: Cannot assign {self.curr_type} to {declared_type}', var_decl.var_def.var_name)
                    if(declared_type.is_array != self.curr_type.is_array):
                        self.error(f'Type mismatch: Cannot assign {self.curr_type} to {declared_type}', var_decl.var_def.var_name)

                # add variable to symbol table
                self.symbol_table.add(var_name, var_decl.var_def.data_type)

        # checking non initalized variables
        elif var_decl.expr == None:
            # array case
            if var_decl.var_def.data_type.is_array:

                # Check if variable name exists in the current function symbol table
                if self.symbol_table.exists_in_curr_env(var_name):
                    self.error(f'duplicate variable definition: {var_name}', var_decl.var_def.var_name)

                # Check if the assigned type matches the declared type
                if declared_type.type_name.token_type != self.curr_type.type_name.token_type and self.curr_type.type_name.token_type != TokenType.VOID_TYPE:
                    self.error(f'Type mismatch: Cannot assign {assigned_type} to {declared_type}', var_decl.var_def.var_name)

                # checking compatible data types
                if(declared_type.is_array != self.curr_type.is_array):
                    self.error(f'Type mismatch: Cannot assign {self.curr_type} to {declared_type}', var_decl.var_def.var_name)

                # add to symbol table
                self.symbol_table.add(var_name, var_decl.var_def.data_type)
            else:
                # assigned type == curr type
                assigned_type = self.curr_type

                # Check if variable name exists in the current function symbol table
                if self.symbol_table.exists_in_curr_env(var_name):
                    self.error(f'duplicate variable definition: {var_name}', var_decl.var_def.var_name)
                
                # add to symbol table
                self.symbol_table.add(var_name, var_decl.var_def.data_type)
        
        
    def visit_assign_stmt(self, assign_stmt):
        # checking use before def
        if not (self.symbol_table.exists_in_curr_env(assign_stmt.lvalue[0].var_name.lexeme)):
            self.error("Use before def in this enviornment", None)

        # finding variable information for left side in the symbol table
        lhs_type = self.symbol_table.get(assign_stmt.lvalue[0].var_name.lexeme)

        # if the lhs is of type array
        if assign_stmt.lvalue[0].array_expr != None:
            # if the flag is not set, error
            if lhs_type.is_array != True:
                self.error("Variable must be of type array", None)
            
            # accept expression inside array []
            assign_stmt.lvalue[0].array_expr.accept(self)

            # saving rhs
            rhs_type = self.curr_type

            # if it is not an int in the array expression or the flag is false, error again
            if(rhs_type.type_name.lexeme != 'int') or (rhs_type.is_array != False):
                self.error("array expressions have to be ints", None)
            
            # setting lhs to the checked data type
            lhs_type = DataType(False, lhs_type.type_name)

        # running through lhs values
        for i in range(1, len(assign_stmt.lvalue)):

            # if the declared type is not in structs, error
            if not (lhs_type.type_name.lexeme in self.structs):
                self.error("undefined struct", None)
            
            # finding current struct
            curr_struct = self.structs[lhs_type.type_name.lexeme]

            # flag to check for correct fields
            valid_field = False
            # itereating through struct fields
            for field in curr_struct.fields:

                # if the field type is the same as the assigned field type
                if(assign_stmt.lvalue[i].var_name.lexeme == field.var_name.lexeme):

                    # if the assigned types array has o expr but the fields type is declared as an array, error
                    if(assign_stmt.lvalue[i].array_expr == None) and (field.data_type.is_array == True):
                        self.error("field type does not match", None)

                    # setting flag as valid field type has been found
                    valid_field = True

                    # setting lhs_type to the fields data_type
                    lhs_type = field.data_type
            # if the flag is false, then field type is invalid
            if valid_field == False:
                self.error("Not a vaild field in struct", None)
        # if the assign stmt expr is none
        if assign_stmt.expr != None:

            # accept self
            assign_stmt.expr.accept(self)

            # save rhs
            rhs_type = self.curr_type

            # if the type is not null
            if rhs_type.type_name.lexeme != 'void':

                # check both sides are compatible
                if (lhs_type.type_name.lexeme != rhs_type.type_name.lexeme):
                    self.error("Variables do not match", None)
            
    def visit_while_stmt(self, while_stmt):

        self.symbol_table.push_environment()

        # accepting while condition
        while_stmt.condition.accept(self)

        # ensuring there is a condition
        if while_stmt.condition == None:
            self.error(f'While loops must include conditional', while_stmt.condition)
        
        # checking the current condition type
        condition_type = self.curr_type

        # Check if the condition is of type bool, error if not
        if (condition_type.type_name.token_type != TokenType.BOOL_TYPE and condition_type.type_name.token_type != TokenType.BOOL_VAL) or condition_type.is_array == True:
            self.error("Condition in while statement must be of type bool", condition_type.type_name)
            

        # Visit the statements inside the while block
        self.symbol_table.push_environment()
        for stmt in while_stmt.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()
        
        
        self.symbol_table.pop_environment()

    def visit_try_catch(self, try_stmt):
        self.symbol_table.push_environment()

        self.symbol_table.push_environment()
        for stmt in try_stmt.try_part.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()

        self.symbol_table.push_environment()
        for stmt in try_stmt.catch_parts.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()


        self.symbol_table.pop_environment()

        
        

        
    def visit_for_stmt(self, for_stmt):

        self.symbol_table.push_environment()

        # ensuring all components in the loop are there
        if for_stmt.var_decl is None:
            self.error("For loops must include a variable declaration", for_stmt.var_decl)
        if for_stmt.condition is None:
            self.error("For loops must include a conditon", for_stmt.condition)
        if for_stmt.assign_stmt is None:
            self.error("For loops must include a assign sttement", for_stmt.assign_stmt)

        # accepting the var_decl
        for_stmt.var_decl.accept(self)

        # accepting the var_decl
        for_stmt.condition.accept(self)

        # store current type before calling assign
        condition_type = self.curr_type

        # Check if the condition is of type bool
        if (condition_type.type_name.token_type != TokenType.BOOL_TYPE and condition_type.type_name.token_type != TokenType.BOOL_VAL) or condition_type.is_array == True:
            self.error("Condition in for statement must be of type bool", condition_type.type_name)

        # if there is no op in the expr, it is not type bool
        if for_stmt.condition.op == None:
            self.error("for statement must be a conditional", condition_type.type_name)
            
        for_stmt.assign_stmt.accept(self)

        # accepting stmts in for loops
        self.symbol_table.push_environment()
        for stmt in for_stmt.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()


        self.symbol_table.pop_environment()

        
        
    def visit_if_stmt(self, if_stmt):

        self.symbol_table.push_environment()

        # accepting the if part condition of if statement
        if_stmt.if_part.condition.accept(self)

        # if there is no condition in if, error
        if if_stmt.if_part.condition == None:
            self.error(f"if statements require a condition!", if_stmt.if_part.condition)


        # Retrieve the type of the condition expression
        condition_type = self.curr_type
        
        # Check if the condition is of type bool
        if (condition_type.type_name.token_type != TokenType.BOOL_TYPE and condition_type.type_name.token_type != TokenType.BOOL_VAL) or condition_type.is_array == True:
            self.error("Condition in if statement must be of type bool", condition_type.type_name)
        
        # Visit the statements inside the if block
        self.symbol_table.push_environment()
        for stmt in if_stmt.if_part.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()
        
               
        self.symbol_table.pop_environment()

        # checking if there are else ifs
        if if_stmt.else_ifs:
            self.symbol_table.push_environment()
            # Visit the else-if parts, if any
            for else_if_part in if_stmt.else_ifs:
                
                # accepting else if condition
                else_if_part.condition.accept(self)

                # finding current type to ensure it is a bool
                condition_type = self.curr_type

                # checking correct expr type
                if (condition_type.type_name.token_type != TokenType.BOOL_TYPE and condition_type.type_name.token_type != TokenType.BOOL_VAL) or condition_type.is_array == True:
                    self.error("Condition in else-if statement must be of type bool", condition_type.type_name)

                # Visit the statements inside the else if block
                self.symbol_table.push_environment()
                for stmt in else_if_part.stmts:
                    stmt.accept(self)
                self.symbol_table.pop_environment()
                
            self.symbol_table.pop_environment()
        
        if if_stmt.else_stmts:
            self.symbol_table.push_environment
            # Visit the else statements, if any
            for stmt in if_stmt.else_stmts:
                stmt.accept(self)
            self.symbol_table.pop_environment()
            
        
        
    def visit_call_expr(self, call_expr):

        # ensuring function that is being called is declared
        if call_expr.fun_name.lexeme not in self.functions and call_expr.fun_name.lexeme not in BUILT_INS:
            self.error(f'{call_expr.fun_name} is not declared', call_expr.fun_name)

        # checking built ins
        if call_expr.fun_name.lexeme in BUILT_INS:
            if call_expr.fun_name.lexeme == 'print':
                # the number of parameters expected by the function
                expected_params = 1
                
                # Get the number of arguments provided in the function call
                provided_args = len(call_expr.args)
                
                # Check if the number of arguments matches the number of parameters
                if provided_args != expected_params:
                    self.error(f'Expected {expected_params} arguments, but got {provided_args} for function {call_expr.fun_name.lexeme}', call_expr.fun_name)
                
                # accept the first arguement
                call_expr.args[0].accept(self)

                # if not a literal or base type, error
                if self.curr_type.type_name.token_type == TokenType.ID:
                    self.error("Inccorect print syntax", call_expr.fun_name)

                # if not a literal or base type, error
                if ((self.curr_type.type_name.token_type != TokenType.STRING_VAL and self.curr_type.type_name.token_type != TokenType.STRING_TYPE and self.curr_type.type_name.token_type != TokenType.INT_VAL and self.curr_type.type_name.token_type != TokenType.INT_TYPE and self.curr_type.type_name.token_type != TokenType.DOUBLE_VAL and self.curr_type.type_name.token_type != TokenType.DOUBLE_TYPE and self.curr_type.type_name.token_type != TokenType.BOOL_VAL and self.curr_type.type_name.token_type != TokenType.BOOL_TYPE))or self.curr_type.is_array == True:
                    self.error("Inccorect print syntax", call_expr.fun_name)

                # setting current typ
                self.curr_type = DataType(False, Token(TokenType.VOID_TYPE, 'void',call_expr.fun_name.line, call_expr.fun_name.column))

            if call_expr.fun_name.lexeme == 'input':
                # the number of parameters expected by the function
                expected_params = 0
                
                # Get the number of arguments provided in the function call
                provided_args = len(call_expr.args)
                
                # Check if the number of arguments matches the number of parameters
                if provided_args != expected_params:
                    self.error(f'Expected {expected_params} arguments, but got {provided_args} for function {call_expr.fun_name.lexeme}', call_expr.fun_name)
                self.curr_type = DataType(False, Token(TokenType.STRING_TYPE, 'string',call_expr.fun_name.line, call_expr.fun_name.column))

            if call_expr.fun_name.lexeme == 'stoi':
                expected_params = 1

                provided_args = len(call_expr.args)

                if provided_args != expected_params:
                    self.error(f'Expected {expected_params} arguments, but got {provided_args} for function {call_expr.fun_name.lexeme}', call_expr.fun_name)

                # Ensure that the argument passed is a string
                call_expr.args[0].accept(self)
                if self.curr_type.type_name.token_type != TokenType.STRING_TYPE and self.curr_type.type_name.token_type != TokenType.STRING_VAL:
                    self.error(f'Argument of stoi function must be of type string, but got {self.curr_type.type_name.lexeme}', call_expr.fun_name)
                
                # Assuming the itos function returns an integer, set the current type accordingly
                self.curr_type = DataType(False, Token(TokenType.INT_TYPE, 'int',call_expr.fun_name.line, call_expr.fun_name.column))

            if call_expr.fun_name.lexeme == 'itos':
                # the number of parameters expected by the function
                expected_params = 1
                
                # Get the number of arguments provided in the function call
                provided_args = len(call_expr.args)
                
                # Check if the number of arguments matches the number of parameters
                if provided_args != expected_params:
                    self.error(f'Expected {expected_params} arguments, but got {provided_args} for function {call_expr.fun_name.lexeme}', call_expr.fun_name)

                # Ensure that the argument passed is a int
                call_expr.args[0].accept(self)

                if self.curr_type.type_name.token_type != TokenType.INT_TYPE and self.curr_type.type_name.token_type != TokenType.INT_VAL:
                    self.error(f'Argument of itos function must be of type int, but got {self.curr_type.type_name.lexeme}', call_expr.fun_name)
                
                # Assuming the itos function returns an integer, set the current type accordingly
                self.curr_type = DataType(False, Token(TokenType.STRING_TYPE, 'string',call_expr.fun_name.line, call_expr.fun_name.column))

            if call_expr.fun_name.lexeme == 'itod':
                # the number of parameters expected by the function
                expected_params = 1
                
                # Get the number of arguments provided in the function call
                provided_args = len(call_expr.args)
                
                # Check if the number of arguments matches the number of parameters
                if provided_args != expected_params:
                    self.error(f'Expected {expected_params} arguments, but got {provided_args} for function {call_expr.fun_name.lexeme}', call_expr.fun_name)

                # Ensure that the argument passed is a int
                call_expr.args[0].accept(self)

                if self.curr_type.type_name.token_type != TokenType.INT_TYPE and self.curr_type.type_name.token_type != TokenType.INT_VAL:
                    self.error(f'Argument of itod function must be of type int, but got {self.curr_type.type_name.lexeme}', call_expr.fun_name)
                
                # Assuming the itod function returns an double, set the current type accordingly
                self.curr_type = DataType(False, Token(TokenType.DOUBLE_TYPE, 'string',call_expr.fun_name.line, call_expr.fun_name.column))


            if call_expr.fun_name.lexeme == 'dtoi':
                # the number of parameters expected by the function
                expected_params = 1
                
                # Get the number of arguments provided in the function call
                provided_args = len(call_expr.args)
                
                # Check if the number of arguments matches the number of parameters
                if provided_args != expected_params:
                    self.error(f'Expected {expected_params} arguments, but got {provided_args} for function {call_expr.fun_name.lexeme}', call_expr.fun_name)

                # Ensure that the argument passed is a double
                call_expr.args[0].accept(self)
                if self.curr_type.type_name.token_type != TokenType.DOUBLE_TYPE and self.curr_type.type_name.token_type != TokenType.DOUBLE_VAL:
                    self.error(f'Argument of dtoi function must be of type double, but got {self.curr_type.type_name.lexeme}', call_expr.fun_name)
                
                # Assuming the dtoi function returns an integer, set the current type accordingly
                self.curr_type = DataType(False, Token(TokenType.INT_TYPE, 'int',call_expr.fun_name.line, call_expr.fun_name.column))

            if call_expr.fun_name.lexeme == 'dtos':
                # the number of parameters expected by the function
                expected_params = 1
                
                # Get the number of arguments provided in the function call
                provided_args = len(call_expr.args)
                
                # Check if the number of arguments matches the number of parameters
                if provided_args != expected_params:
                    self.error(f'Expected {expected_params} arguments, but got {provided_args} for function {call_expr.fun_name.lexeme}', call_expr.fun_name)

                # Ensure that the argument passed is a double
                call_expr.args[0].accept(self)

                if self.curr_type.type_name.token_type != TokenType.DOUBLE_TYPE and self.curr_type.type_name.token_type != TokenType.DOUBLE_VAL:
                    self.error(f'Argument of dtos function must be of type double, but got {self.curr_type.type_name.lexeme}', call_expr.fun_name)
                
                # Assuming the dtos function returns an string, set the current type accordingly
                self.curr_type = DataType(False, Token(TokenType.STRING_TYPE, 'string',call_expr.fun_name.line, call_expr.fun_name.column))

            if call_expr.fun_name.lexeme == 'stod':
                # the number of parameters expected by the function
                expected_params = 1
                
                # Get the number of arguments provided in the function call
                provided_args = len(call_expr.args)
                
                # Check if the number of arguments matches the number of parameters
                if provided_args != expected_params:
                    self.error(f'Expected {expected_params} arguments, but got {provided_args} for function {call_expr.fun_name.lexeme}', call_expr.fun_name)

                # Ensure that the argument passed is a string
                call_expr.args[0].accept(self)

                if self.curr_type.type_name.token_type != TokenType.STRING_TYPE and self.curr_type.type_name.token_type != TokenType.STRING_VAL:
                    self.error(f'Argument of dtos function must be of type double, but got {self.curr_type.type_name.lexeme}', call_expr.fun_name)
                
                # Assuming the stod function returns an double, set the current type accordingly
                self.curr_type = DataType(False, Token(TokenType.DOUBLE_TYPE, 'double',call_expr.fun_name.line, call_expr.fun_name.column))


            if call_expr.fun_name.lexeme == 'length':
                # the number of parameters expected by the function
                expected_params = 1
                
                # Get the number of arguments provided in the function call
                provided_args = len(call_expr.args)
                
                # Check if the number of arguments matches the number of parameters
                if provided_args != expected_params:
                    self.error(f'Expected {expected_params} arguments, but got {provided_args} for function {call_expr.fun_name.lexeme}', call_expr.fun_name)
                
                call_expr.args[0].accept(self)

                if self.curr_type.is_array == False:
                    if self.curr_type.type_name.token_type == TokenType.DOUBLE_VAL or self.curr_type.type_name.token_type == TokenType.INT_VAL or self.curr_type.type_name.token_type == TokenType.INT_TYPE or self.curr_type.type_name.token_type == TokenType.DOUBLE_TYPE:
                        self.error(f'Argument of length function parameter cannot be double or int primitive, but got {self.curr_type.type_name.lexeme}', call_expr.fun_name)
                self.curr_type = DataType(False, Token(TokenType.INT_TYPE, 'int',call_expr.fun_name.line, call_expr.fun_name.column))
                
            if call_expr.fun_name.lexeme == 'get':
                # the number of parameters expected by the function
                expected_params = 2
                
                # Get the number of arguments provided in the function call
                provided_args = len(call_expr.args)
                
                # Check if the number of arguments matches the number of parameters
                if provided_args != expected_params:
                    self.error(f'Expected {expected_params} arguments, but got {provided_args} for function {call_expr.fun_name.lexeme}', call_expr.fun_name)
                                
                call_expr.args[0].accept(self)
                if self.curr_type.type_name.token_type != TokenType.INT_TYPE and self.curr_type.type_name.token_type != TokenType.INT_VAL:
                    self.error(f'Argument of get function parameter must int primitive or int, but got {self.curr_type.type_name.lexeme}', call_expr.fun_name)
                
                call_expr.args[1].accept(self)
                if self.curr_type.type_name.token_type != TokenType.STRING_TYPE and self.curr_type.type_name.token_type != TokenType.STRING_VAL or self.curr_type.is_array == True:
                    self.error(f'Argument of get function parameter must int primitive or int, but got {self.curr_type.type_name.lexeme}', call_expr.fun_name)
                self.curr_type = DataType(False, Token(TokenType.STRING_TYPE, 'string',call_expr.fun_name.line, call_expr.fun_name.column))
                
        else:
            # save function name
            fun_name = call_expr.fun_name.lexeme

            # find the function in the functions list
            fun_def = self.functions[fun_name]

            # ensure there is a valid amount of params
            if len(call_expr.args) != len(fun_def.params):
                self.error(f'Expected {len(fun_def.params)} arguments, but got {len(call_expr.args)} for function {call_expr.fun_name.lexeme}', call_expr.fun_name)

            # ensure that params are typed well and compatible
            for i in range(len(call_expr.args)):
                param_type = fun_def.params[i].data_type
                call_expr.args[i].accept(self)
                if(param_type.type_name.token_type != self.curr_type.type_name.token_type and self.curr_type.type_name.token_type != TokenType.VOID_TYPE):
                    self.error("Wrong datatype for parameter!: ", call_expr.fun_name)

            # setting current type
            self.curr_type = fun_def.return_type


    def visit_expr(self, expr):
        # check the first term
        expr.first.accept(self)
        # record the lhs type
        lhs_type = self.curr_type

        # check if more to expression
        if expr.op:
            # check rest of expression
            expr.rest.accept(self)
            # record the rhs type
            rhs_type = self.curr_type

            # Perform type checking based on the operator and operand types
            if expr.op.lexeme == '+':
                # Addition operator
                if lhs_type.type_name.lexeme == 'string' and rhs_type.type_name.lexeme == 'string':
                    self.curr_type = DataType(False, Token(TokenType.STRING_TYPE, 'string', rhs_type.type_name.line, rhs_type.type_name.column))

                elif lhs_type.type_name.lexeme == 'double' and rhs_type.type_name.lexeme == 'double':
                    self.curr_type = DataType(False, Token(TokenType.DOUBLE_TYPE, 'double', rhs_type.type_name.line, rhs_type.type_name.column))

                elif lhs_type.type_name.lexeme == 'int' and rhs_type.type_name.lexeme == 'int':
                    self.curr_type = DataType(False, Token(TokenType.INT_TYPE, 'int', rhs_type.type_name.line, rhs_type.type_name.column))
                else:
                    self.error("Incorrect datatype for operator", expr.op)

            # checking expressions for operators that are not plusses
            if expr.op.lexeme in OPERATORS_NO_PLUS:
                
                if lhs_type.type_name.lexeme == 'double' and rhs_type.type_name.lexeme == 'double':
                    self.curr_type = DataType(False, Token(TokenType.DOUBLE_TYPE, 'double', rhs_type.type_name.line, rhs_type.type_name.column))

                elif lhs_type.type_name.lexeme == 'int' and rhs_type.type_name.lexeme == 'int':
                    self.curr_type = DataType(False, Token(TokenType.INT_TYPE, 'int', rhs_type.type_name.line, rhs_type.type_name.column))
                else:
                    self.error("Incorrect datatype for operator ", expr.op)
            
            # looking through relational operators
            if expr.op.lexeme in CONDITIONAL_NON_BOOL_RHS_LHS:
                if expr.op.lexeme == '==' or expr.op.lexeme == '!=':
                    if ((lhs_type.type_name.token_type != TokenType.VOID_TYPE) or (rhs_type.type_name.token_type != TokenType.VOID_TYPE)):
                        
                        if (lhs_type.type_name.token_type != rhs_type.type_name.token_type):
                            if(lhs_type.type_name.token_type == TokenType.VOID_TYPE or rhs_type.type_name.token_type == TokenType.VOID_TYPE):
                                self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', rhs_type.type_name.line, rhs_type.type_name.column))
                            else:
                                self.error(f"Incorrect usage of bool comparision: '{expr.op.lexeme}'", expr.op)
                        else:
                            self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', rhs_type.type_name.line, rhs_type.type_name.column))
                        
                elif lhs_type.type_name.token_type == TokenType.DOUBLE_TYPE and rhs_type.type_name.token_type == TokenType.DOUBLE_TYPE:
                    self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', rhs_type.type_name.line, rhs_type.type_name.column))

                elif lhs_type.type_name.token_type == TokenType.INT_TYPE and rhs_type.type_name.token_type == TokenType.INT_TYPE:
                    self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', rhs_type.type_name.line, rhs_type.type_name.column))\
                
                elif lhs_type.type_name.token_type == TokenType.STRING_TYPE and rhs_type.type_name.token_type == TokenType.STRING_TYPE:
                    self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', rhs_type.type_name.line, rhs_type.type_name.column))
                
                elif lhs_type.type_name.lexeme == 'bool' and rhs_type.type_name.lexeme == 'bool' and expr.op.lexeme in CONDITIONAL_BOOL_RHS_LHS:
                    self.error(f"Incorrect usage of bool comparision: '{expr.op.lexeme}'", expr.op)

            # looking through comparison operators
            if expr.op.lexeme in COMPAIRSON_OPERATORS:
                if lhs_type.type_name.token_type == TokenType.BOOL_TYPE and rhs_type.type_name.token_type == TokenType.BOOL_TYPE:
                    self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', rhs_type.type_name.line, rhs_type.type_name.column))
                else:
                    self.error(f"Incorrect usage of bool comparision: '{expr.op.lexeme}'", expr.op)


        # check not operation
        if expr.not_op:
            # Check if there is an expression after 'not'
            if expr.rest is not None:

                # Accept the rest of the expression after 'not'
                expr.rest.accept(self) 

                # savin rhs_type
                rhs_type = self.curr_type

                # rechecking the same checks above
                if expr.op.lexeme in CONDITIONAL_NON_BOOL_RHS_LHS:
                    if expr.op.lexeme in CONDITIONAL_NON_BOOL_RHS_LHS:
                        if expr.op.lexeme == '==' or expr.op.lexeme == '!=':
                            if ((lhs_type.type_name.token_type != TokenType.VOID_TYPE) or (rhs_type.type_name.token_type != TokenType.VOID_TYPE)):
                                
                                if (lhs_type.type_name.token_type != rhs_type.type_name.token_type):
                                    if(lhs_type.type_name.token_type == TokenType.VOID_TYPE or rhs_type.type_name.token_type == TokenType.VOID_TYPE):
                                        self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', rhs_type.type_name.line, rhs_type.type_name.column))
                                    else:
                                        self.error(f"Incorrect usage of bool comparision: '{expr.op.lexeme}'", expr.op)
                                else:
                                    self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', rhs_type.type_name.line, rhs_type.type_name.column))
                    if lhs_type.type_name.lexeme == 'double' and rhs_type.type_name.lexeme == 'double':
                        self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', rhs_type.type_name.line, rhs_type.type_name.column))

                    elif lhs_type.type_name.lexeme == 'int' and rhs_type.type_name.lexeme == 'int':
                        self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', rhs_type.type_name.line, rhs_type.type_name.column))
                    
                    elif lhs_type.type_name.lexeme == 'bool' and rhs_type.type_name.lexeme == 'bool' and expr.op.lexeme in CONDITIONAL_BOOL_RHS_LHS:
                        self.error(f"Incorrect usage of bool comparision: '{expr.op.lexeme}'", expr.op)


    def visit_data_type(self, data_type):
        # note: allowing void (bad cases of void caught by parser)
        name = data_type.type_name.lexeme
        if (name == 'void' or name in BASE_TYPES or name in self.structs) and data_type.is_array == False:
            self.curr_type = data_type    
        else: 
            self.error(f'invalid type "{name}"', data_type.type_name)
            
    
    def visit_var_def(self, var_def):
        var_def.data_type.accept(self)

         # Add the variable definition to the symbol table
        self.symbol_table.add(var_def.var_name.lexeme, var_def.data_type)

        
    def visit_simple_term(self, simple_term):
        # accepting simple term
        if simple_term.rvalue:
            simple_term.rvalue.accept(self)
        else:
            self.error("Incorrect simple term syntax", simple_term.rvalue)
    
    def visit_complex_term(self, complex_term):
        # accepting complex term
        if complex_term.expr:
            complex_term.expr.accept(self)
        else:
            self.error("Incorrect complex term syntax", complex_term.expr)
        

    def visit_simple_rvalue(self, simple_rvalue):
        value = simple_rvalue.value
        line = simple_rvalue.value.line
        column = simple_rvalue.value.column
        type_token = None 
        if value.token_type == TokenType.INT_VAL:
            type_token = Token(TokenType.INT_TYPE, 'int', line, column)
        elif value.token_type == TokenType.DOUBLE_VAL:
            type_token = Token(TokenType.DOUBLE_TYPE, 'double', line, column)
        elif value.token_type == TokenType.STRING_VAL:
            type_token = Token(TokenType.STRING_TYPE, 'string', line, column)
        elif value.token_type == TokenType.BOOL_VAL:
            type_token = Token(TokenType.BOOL_TYPE, 'bool', line, column)
        elif value.token_type == TokenType.NULL_VAL:
            type_token = Token(TokenType.VOID_TYPE, 'void', line, column)
        self.curr_type = DataType(False, type_token)

        
    def visit_new_rvalue(self, new_rvalue):
        # finding the struct we are currently in
        struct_def = self.structs.get(new_rvalue.type_name.lexeme)

        # if no struct is found and there is no array expr, error
        if struct_def is None and new_rvalue.array_expr == None:
            self.error(f"Undefined struct type '{new_rvalue.type_name.lexeme}'", new_rvalue.type_name)
        else:

            # array case
            if new_rvalue.array_expr != None:

                # find expression
                new_rvalue.array_expr.accept(self)

                # saving array expr type
                array_expr_type = self.curr_type.type_name.token_type

                # ensuring that array expression is a non array int value
                if array_expr_type != TokenType.INT_TYPE and array_expr_type != TokenType.INT_VAL:
                    self.error("Array size must be and integer", new_rvalue.type_name)

                # setting current data type
                self.curr_type = DataType(True, new_rvalue.type_name)
            
            else:

                # saving field length in declared struct
                field_length = len(new_rvalue.struct_params)
                # saving length found in struct list
                struct_length = len(struct_def.fields)

                # if param length are not the same, error
                if field_length != struct_length:
                    self.error("Incorrect amount of fields!", new_rvalue.type_name)
                
                # type checking struct params to ensure the allign
                for i in range (0, len(new_rvalue.struct_params)):

                    # acceting field
                    new_rvalue.struct_params[i].accept(self)

                    # if field is not void and not compatible, error
                    if self.curr_type.type_name.lexeme != 'void':
                        if self.curr_type.type_name.lexeme != struct_def.fields[i].data_type.type_name.lexeme or self.curr_type.is_array != struct_def.fields[i].data_type.is_array:
                            self.error("Incorrect field type", new_rvalue.type_name)
                            
                # settng current type
                self.curr_type = DataType(False, new_rvalue.type_name)

        
            
    def visit_var_rvalue(self, var_rvalue):
        # ensuring that the variable referenced exists, if not error
        if not (self.symbol_table.exists(var_rvalue.path[0].var_name.lexeme)):
            self.error("Use before def error, this variable has not been defined yet", var_rvalue.path[0].var_name)
        
        # grabbing data type from the symbol table
        data_type = self.symbol_table.get(var_rvalue.path[0].var_name.lexeme)

        # if the variable is an array case
        if var_rvalue.path[0].array_expr != None:

            # ensure that the assigned type is of array, error if not
            if data_type.is_array != True:
                self.error('data type must be of array type', var_rvalue.path[0].var_name)
            
            # get array expr
            var_rvalue.path[0].array_expr.accept(self)

            # save the right hand side type
            rhs_type = self.curr_type

            # type checking array expresson to ensure it is an int and not an array
            if(rhs_type.type_name.lexeme != 'int') or (rhs_type.is_array != False):
                self.error("Type mismatch, arrays expressions must be ints", var_rvalue.path[0].var_name)

            # setting data type
            data_type = DataType(False, data_type.type_name)
        
        # running through the path starting at the second spot
        for i in range(1, len(var_rvalue.path)):
            # if the data type is not in structs, error
            if not (data_type.type_name.lexeme in self.structs):
                self.error("variable must be a struct", var_rvalue.path[i].var_name)

            # find current struct
            curr_struct = self.structs[data_type.type_name.lexeme]

            # set flag for a valid field
            valid_field = False

            # checking fields in struct
            for field in curr_struct.fields:

                # if the paths data type equals the set field type, set flag true
                if var_rvalue.path[i].var_name.lexeme == field.var_name.lexeme:
                    valid_field = True
                    data_type = field.data_type
            # checking the flag
            if valid_field == False:
                self.error("Not a valid field type", var_rvalue.path[i].var_name)

        # setting current type
        self.curr_type = data_type