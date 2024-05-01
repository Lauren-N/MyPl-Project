"""IR code generator for converting MyPL to VM Instructions. 

NAME: Lauren Nguyen
DATE: Spring 2024
CLASS: CPSC 326

"""

from mypl_token import *
from mypl_ast import *
from mypl_var_table import *
from mypl_frame import *
from mypl_opcode import *
from mypl_vm import *


class CodeGenerator (Visitor):

    def __init__(self, vm):
        """Creates a new Code Generator given a VM. 
        
        Args:
            vm -- The target vm.
        """
        # the vm to add frames to
        self.vm = vm
        # the current frame template being generated
        self.curr_template = None
        # for var -> index mappings wrt to environments
        self.var_table = VarTable()
        # struct name -> StructDef for struct field info
        self.struct_defs = {}

    
    def add_instr(self, instr):
        """Helper function to add an instruction to the current template."""
        self.curr_template.instructions.append(instr)

        
    def visit_program(self, program):
        for struct_def in program.struct_defs:
            struct_def.accept(self)
        for fun_def in program.fun_defs:
            fun_def.accept(self)

    
    def visit_struct_def(self, struct_def):
        # remember the struct def for later
        self.struct_defs[struct_def.struct_name.lexeme] = struct_def

        
    def visit_fun_def(self, fun_def):
        # creating a new template for a new function
        self.curr_template = VMFrameTemplate(fun_def.fun_name.lexeme, 0, [])

        # pushing new enviorment through var table
        self.var_table.push_environment()

        # if params are present
        if fun_def.params != []:
            
            # variable to record arg count
            arg_count = 0

            # running through each parameter
            for i in range(0, len(fun_def.params)):

                # accepting param
                fun_def.params[i].accept(self)

                # adding param name to var table
                self.var_table.add(fun_def.params[i].var_name.lexeme)

                # finding index it was stored at
                j = self.var_table.get(fun_def.params[i].var_name.lexeme)

                # storing on the stack
                self.add_instr(STORE(j))

                # add to arg_count
                arg_count += 1
            
            # setting new arg count on the template
            self.curr_template.arg_count = arg_count
        
        # stmt list to hold length
        stmt_list = []

        # accepting all stmts in function
        for stmt in fun_def.stmts:

            # accepting
            stmt.accept(self)

            # appending to list to keep count
            stmt_list.append(stmt)

        # finding length of statements in func
        length = len(stmt_list)

        # if there are no arguements, no return statement is present, push one
        if length == 0:
            self.add_instr(PUSH(None))
            self.add_instr(RET())
        
        # making sure the last statement is return statement, if not, push one
        elif not isinstance(stmt_list[length-1], ReturnStmt):
            self.add_instr(PUSH(None))
            self.add_instr(RET())

        # pop environment
        self.var_table.pop_environment()

        # adding frame to the vm
        self.vm.add_frame_template(self.curr_template)
    
    def visit_return_stmt(self, return_stmt):

        # accepting return
        return_stmt.expr.accept(self)

        # addign return
        self.add_instr(RET())

        
    def visit_var_decl(self, var_decl):

        # if there is an expr after assign
        if var_decl.expr:

            # accept expr, push what ever is assigned onto stack
            var_decl.expr.accept(self)
        else:

            # otherwise push Null
            self.add_instr(PUSH(None))
        
        # adding the var name into the var_table
        self.var_table.add(var_decl.var_def.var_name.lexeme)

        # finding the index it was inserted in
        i = self.var_table.get(var_decl.var_def.var_name.lexeme)

        # storing the variable at index found
        self.add_instr(STORE(i))


    
    def visit_assign_stmt(self, assign_stmt):

        # if path is one
        if len(assign_stmt.lvalue) == 1:
            # index to load from
            i = self.var_table.get(assign_stmt.lvalue[0].var_name.lexeme)

            # array case
            if assign_stmt.lvalue[0].array_expr != None:
                # loading from index found
                self.add_instr(LOAD(i))

                # getting array expr
                assign_stmt.lvalue[0].array_expr.accept(self)

                # accepting val
                assign_stmt.expr.accept(self)

                # setting index
                self.add_instr(SETI())
            # basic assign stmt
            else:
                assign_stmt.expr.accept(self)
                self.add_instr(STORE(i))

        # structs
        else:
            # if there is no array in the first spot in path
            if assign_stmt.lvalue[0].array_expr == None:
                oid = self.var_table.get(assign_stmt.lvalue[0].var_name.lexeme)
                self.add_instr(LOAD(oid))
                curr_field = assign_stmt.lvalue[-1].var_name.lexeme
                for i in range(1, len(assign_stmt.lvalue) - 1):
                    self.add_instr(GETF(assign_stmt.lvalue[i].var_name.lexeme))
                assign_stmt.expr.accept(self)
                self.add_instr(SETF(curr_field))

            # if there is an array in the first path
            else:
                i = self.var_table.get(assign_stmt.lvalue[0].var_name.lexeme)
                self.add_instr(LOAD(i))
                assign_stmt.lvalue[0].array_expr.accept(self)
                self.add_instr(GETI())
                curr_field = assign_stmt.lvalue[-1].var_name.lexeme

                for i in range(1, len(assign_stmt.lvalue) - 1):
                    oid = self.var_table.get(assign_stmt.lvalue[i].var_name.lexeme)
                    self.add_instr(LOAD(oid))
                    self.add_instr(GETF(assign_stmt.lvalue[i].var_name.lexeme))
                    
                assign_stmt.expr.accept(self)
                self.add_instr(SETF(curr_field))

    def visit_try_catch_stmt(self, try_stmt):
        # pushing enviorment to accept stmts
        self.var_table.push_environment()

        # setting try flag
        self.add_instr(TRY_START())

        # accepting statements
        for stmt in try_stmt.try_part:
            stmt.accept(self)
        
        # setting try flag false
        self.add_instr(TRY_END())

        # popping environment
        self.var_table.pop_environment()

        # pushing enviorment to accept stmts
        self.var_table.push_environment()

        self.add_instr(CATCH_START())
        # accepting statements
        for stmt in try_stmt.catch_parts:
            stmt.accept(self)

        self.add_instr(CATCH_END())
        # popping environment
        self.var_table.pop_environment()
    
    def visit_while_stmt(self, while_stmt):

        # saving index to jump back to
        stored_index = len(self.curr_template.instructions) 

        # accepting condition
        while_stmt.condition.accept(self)

        # creating jump_instr with a dummy value
        jump_instr = JMPF(-1)

        # adding instr to the stack
        self.add_instr(jump_instr)

        # pushing enviorment to accept stmts
        self.var_table.push_environment()

        # accepting statements
        for stmt in while_stmt.stmts:
            stmt.accept(self)

        # popping environment
        self.var_table.pop_environment()
        
        # jumping back to the previous index AKA where the condition starts
        self.add_instr(JMP(stored_index))

        # adding landing spot for JMPF
        self.add_instr(NOP())

        # setting operand of jump instr to the end of the stack where NOP is
        jump_instr.operand = len(self.curr_template.instructions) - 1

        

        
    def visit_for_stmt(self, for_stmt):

        # pushing enviorment for var_decl
        self.var_table.push_environment()

        # accepting var decl
        for_stmt.var_decl.accept(self)

        # storing index where we need to jump back to to loop
        stored_index = len(self.curr_template.instructions)

        # accepting condition
        for_stmt.condition.accept(self)

        # setting dummy value for JMPF
        jump_instr = JMPF(-1)

        # adding instr to stack
        self.add_instr(jump_instr)

        # accepting stmts
        self.var_table.push_environment()
        for stmt in for_stmt.stmts:
            stmt.accept(self)
        self.var_table.pop_environment()

        # accepting assign stmt AFTER stmts
        for_stmt.assign_stmt.accept(self)

        # jump back to stored index
        self.add_instr(JMP(stored_index))

        # pushing landing spot for JMPF
        self.add_instr(NOP())

        # setting jump instr to where NOP is
        jump_instr.operand = len(self.curr_template.instructions) - 1

        # popping enviorment
        self.var_table.pop_environment()

    
    def visit_if_stmt(self, if_stmt):

        # basic ifs
        if if_stmt.else_ifs == [] and if_stmt.else_stmts == []:
            jump_instr = JMPF(-1)

            if_stmt.if_part.condition.accept(self)
            self.add_instr(jump_instr)

            self.var_table.push_environment()
            for stmt in if_stmt.if_part.stmts:
                stmt.accept(self)
            self.var_table.pop_environment()
            self.add_instr(NOP())
            jump_instr.operand = len(self.curr_template.instructions) - 1

        # ifs and elses
        elif if_stmt.else_ifs == [] and if_stmt.else_stmts != []:
            jump_instr = JMPF(-1)

            if_stmt.if_part.condition.accept(self)
            self.add_instr(jump_instr)

            self.var_table.push_environment()
            for stmt in if_stmt.if_part.stmts:
                stmt.accept(self)
            self.var_table.pop_environment()
            self.add_instr(NOP())
            jump_instr.operand = len(self.curr_template.instructions) - 1

            self.var_table.push_environment()
            for stmt in if_stmt.else_stmts:
                stmt.accept(self)
            self.var_table.pop_environment()

        # full if statement
        elif if_stmt.else_ifs != [] and if_stmt.else_stmts != []:
            jump_instr = JMPF(-1)

            if_stmt.if_part.condition.accept(self)
            self.add_instr(jump_instr)

            self.var_table.push_environment()
            for stmt in if_stmt.if_part.stmts:
                stmt.accept(self)
            self.var_table.pop_environment()
            self.add_instr(NOP())

            jump_instr.operand = len(self.curr_template.instructions) - 1

            for i in range(0, len(if_stmt.else_ifs)):
                if_stmt.else_ifs[i].condition.accept(self)
                self.add_instr(jump_instr)

                self.var_table.push_environment()
                for stmt in if_stmt.else_ifs[i].stmts:
                    stmt.accept(self)
                self.var_table.pop_environment()
                
                self.add_instr(NOP())


            self.var_table.push_environment()
            for stmt in if_stmt.else_stmts:
                stmt.accept(self)
            self.var_table.pop_environment()

            self.add_instr(NOP())
            jump_instr.operand = len(self.curr_template.instructions) - 1



    def visit_call_expr(self, call_expr):
        # print
        if call_expr.fun_name.lexeme == 'print':
            for i in range(0, len(call_expr.args)):
                call_expr.args[i].accept(self)
            self.add_instr(WRITE())

        # STOI
        elif call_expr.fun_name.lexeme == 'stoi':
            call_expr.args[0].accept(self)
            self.add_instr(TOINT())

        # DTOI
        elif call_expr.fun_name.lexeme == 'dtoi':
            call_expr.args[0].accept(self)
            self.add_instr(TOINT())

        # STOD
        elif call_expr.fun_name.lexeme == 'stod':
            call_expr.args[0].accept(self)
            self.add_instr(TODBL())

        # DTOS
        elif call_expr.fun_name.lexeme == 'dtos':
            call_expr.args[0].accept(self)
            self.add_instr(TOSTR())

        # ITOD
        elif call_expr.fun_name.lexeme == 'itod':
            call_expr.args[0].accept(self)
            self.add_instr(TODBL())

        # ITOS
        elif call_expr.fun_name.lexeme == 'itos':
            call_expr.args[0].accept(self)
            self.add_instr(TOSTR())

        # INPUT
        elif call_expr.fun_name.lexeme == 'input':
            self.add_instr(READ())

        # LEN
        elif call_expr.fun_name.lexeme == 'length':
            call_expr.args[0].accept(self)
            self.add_instr(LEN())

        # GET
        elif call_expr.fun_name.lexeme == 'get':
            call_expr.args[0].accept(self)
            call_expr.args[1].accept(self)
            self.add_instr(GETC())
 
        # Non built in function calls
        else:
            for i in range (len(call_expr.args)):
                call_expr.args[i].accept(self)
            self.add_instr(CALL(call_expr.fun_name.lexeme))

        
    def visit_expr(self, expr):

        # checking if expr is more than a simple r value
        if expr.op:

            # ADDITION
            if expr.op.lexeme == '+':
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(ADD())

            # SUBTRACTION
            elif expr.op.lexeme == '-':
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(SUB())

            # DIVISION
            elif expr.op.lexeme == '/':
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(DIV())

            # MULTIPLICATION
            elif expr.op.lexeme == '*':
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(MUL())

            # LESS THAN
            elif expr.op.lexeme == '<':
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(CMPLT())

            # GREATER THAN
            elif expr.op.lexeme == '>':
                # accepting rest first to achieve "greater than" by comparing second val first
                expr.rest.accept(self)
                expr.first.accept(self)
                self.add_instr(CMPLT())

            # LESS THAN EQUAL TO
            elif expr.op.lexeme == '<=':
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(CMPLE())

            # GREATER THAN EQUAL TO
            elif expr.op.lexeme == '>=':
                # accepting rest first to achieve "greater than" by comparing second val first
                expr.rest.accept(self)
                expr.first.accept(self)
                self.add_instr(CMPLE())

            # AND
            elif expr.op.lexeme == 'and':
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(AND())

            # OR
            elif expr.op.lexeme == 'or':
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(OR())

            # NOT EQUAL TO
            elif expr.op.lexeme == '!=':
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(CMPNE())

            # EQUAL TO
            elif expr.op.lexeme == '==':
                expr.first.accept(self)
                expr.rest.accept(self)
                self.add_instr(CMPEQ())
        # NOT
        elif expr.not_op:
            expr.first.accept(self)
            self.add_instr(NOT())
        
        # SIMPLE R VALUE
        else:
            expr.first.accept(self)

            
    def visit_data_type(self, data_type):
        # nothing to do here
        pass

    
    def visit_var_def(self, var_def):
        # nothing to do here
        pass

    
    def visit_simple_term(self, simple_term):
        simple_term.rvalue.accept(self)

        
    def visit_complex_term(self, complex_term):
        complex_term.expr.accept(self)

        
    def visit_simple_rvalue(self, simple_rvalue):
        val = simple_rvalue.value.lexeme
        if simple_rvalue.value.token_type == TokenType.INT_VAL:
            self.add_instr(PUSH(int(val)))
        elif simple_rvalue.value.token_type == TokenType.DOUBLE_VAL:
            self.add_instr(PUSH(float(val)))
        elif simple_rvalue.value.token_type == TokenType.STRING_VAL:
            val = val.replace('\\n', '\n')
            val = val.replace('\\t', '\t')
            self.add_instr(PUSH(val))
        elif val == 'true':
            self.add_instr(PUSH(True))
        elif val == 'false':
            self.add_instr(PUSH(False))
        elif val == 'null':
            self.add_instr(PUSH(None))

    
    def visit_new_rvalue(self, new_rvalue):
        # struct
        if new_rvalue.array_expr == None:

            # finding current struct we are instantiating
            curr_struct = self.struct_defs[new_rvalue.type_name.lexeme]

            # allocating struct
            self.add_instr(ALLOCS())

            # looking thrrough fields
            for i in range(0, len(curr_struct.fields)):
                self.add_instr(DUP())

                # accepting struct_params
                new_rvalue.struct_params[i].accept(self)

                # finding field name
                field_name = curr_struct.fields[i].var_name.lexeme

                # setting field
                self.add_instr(SETF(field_name))
        else:
            # finding array expr
            new_rvalue.array_expr.accept(self)

            # allocating array
            self.add_instr(ALLOCA())


    
    def visit_var_rvalue(self, var_rvalue):

        # creating flag to find the first expression in path
        cnt = 0

        # iterating through path
        for varref in var_rvalue.path:

            # inital path val
            if cnt == 0:
                # getting the index to load the val
                index = self.var_table.get(varref.var_name.lexeme)
                # loading
                self.add_instr(LOAD(index))

                # if it is an array
                if varref.array_expr != None:

                    # accept the array expr
                    varref.array_expr.accept(self)

                    # get index
                    self.add_instr(GETI())
            else:
                # if it is an array
                if varref.array_expr != None:
                    # if it is not in the var table or in struct_defs
                    if(self.var_table.get(varref.var_name.lexeme) == None) and not (varref.var_name.lexeme in self.struct_defs):

                        # get field
                        self.add_instr(GETF(varref.var_name.lexeme))
                    else:

                        # finding index to load val
                        index = self.var_table.get(varref.var_name.lexeme)

                        # loading val
                        self.add_instr(LOAD(index))
                    
                    # accepting array expr
                    varref.array_expr.accept(self)

                    # getting index of array
                    self.add_instr(GETI())
                else:

                    # get struct field
                    self.add_instr(GETF(varref.var_name.lexeme))
            cnt = cnt + 1

            
                        
