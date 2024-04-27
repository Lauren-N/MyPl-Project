"""Unit tests for CPSC 326 HW-3. 

DISCLAIMER: These are basic tests that DO NOT guarantee correctness of
your code. As unit tests, each test is focused on an isolated part of
your overall solution. It is important that you also ensure your code
works over the example files provided and that you further test your
program beyond the test cases given. Grading of your work may also
involve the use of additional tests beyond what is provided in the
starter code.


NAME: S. Bowers
DATE: Spring 2024
CLASS: CPSC 326

"""

import pytest
import io

from mypl_error import *
from mypl_iowrapper import *
from mypl_token import *
from mypl_lexer import *
from mypl_ast_parser import *


#----------------------------------------------------------------------
# Basic Function Definitions
#----------------------------------------------------------------------

def test_empty_input():
    in_stream = FileWrapper(io.StringIO(''))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 0

def test_empty_fun():
    in_stream = FileWrapper(io.StringIO('int f() {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert len(p.struct_defs) == 0
    assert p.fun_defs[0].return_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].return_type.is_array == False
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert len(p.fun_defs[0].params) == 0
    assert len(p.fun_defs[0].stmts) == 0

def test_empty_fun_array_return():
    in_stream = FileWrapper(io.StringIO('array int f() {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert p.fun_defs[0].return_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].return_type.is_array == True
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert len(p.fun_defs[0].params) == 0
    assert len(p.fun_defs[0].stmts) == 0

def test_empty_fun_one_param():
    in_stream = FileWrapper(io.StringIO('int f(string x) {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert len(p.fun_defs[0].params) == 1
    assert p.fun_defs[0].params[0].data_type.is_array == False
    assert p.fun_defs[0].params[0].data_type.type_name.lexeme == 'string'
    assert p.fun_defs[0].params[0].var_name.lexeme == 'x'    

def test_empty_fun_one_id_param():
    in_stream = FileWrapper(io.StringIO('int f(S s1) {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert len(p.fun_defs[0].params) == 1
    assert p.fun_defs[0].params[0].data_type.is_array == False
    assert p.fun_defs[0].params[0].data_type.type_name.lexeme == 'S'
    assert p.fun_defs[0].params[0].var_name.lexeme == 's1'    

def test_empty_fun_one_array_param():
    in_stream = FileWrapper(io.StringIO('int f(array int ys) {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert len(p.fun_defs[0].params) == 1
    assert p.fun_defs[0].params[0].data_type.is_array == True
    assert p.fun_defs[0].params[0].data_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].params[0].var_name.lexeme == 'ys'    

def test_empty_fun_two_params():
    in_stream = FileWrapper(io.StringIO('int f(bool x, int y) {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert len(p.fun_defs[0].params) == 2
    assert p.fun_defs[0].params[0].data_type.is_array == False
    assert p.fun_defs[0].params[0].data_type.type_name.lexeme == 'bool'
    assert p.fun_defs[0].params[0].var_name.lexeme == 'x'    
    assert p.fun_defs[0].params[1].data_type.is_array == False
    assert p.fun_defs[0].params[1].data_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].params[1].var_name.lexeme == 'y'    

def test_empty_fun_three_params():
    in_stream = FileWrapper(io.StringIO('int f(bool x, int y, array string z) {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert len(p.fun_defs[0].params) == 3
    assert p.fun_defs[0].params[0].data_type.is_array == False
    assert p.fun_defs[0].params[0].data_type.type_name.lexeme == 'bool'
    assert p.fun_defs[0].params[0].var_name.lexeme == 'x'    
    assert p.fun_defs[0].params[1].data_type.is_array == False
    assert p.fun_defs[0].params[1].data_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].params[1].var_name.lexeme == 'y'    
    assert p.fun_defs[0].params[2].data_type.is_array == True
    assert p.fun_defs[0].params[2].data_type.type_name.lexeme == 'string'
    assert p.fun_defs[0].params[2].var_name.lexeme == 'z'    

def test_multiple_empty_funs():
    in_stream = FileWrapper(io.StringIO(
        'void f() {}\n'
        'int g() {}\n'
        ''
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 2
    assert len(p.struct_defs) == 0
    
    
#----------------------------------------------------------------------
# Basic Struct Definitions
#----------------------------------------------------------------------

def test_empty_struct():
    in_stream = FileWrapper(io.StringIO('struct S {}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 1
    assert p.struct_defs[0].struct_name.lexeme == 'S'
    assert len(p.struct_defs[0].fields) == 0

def test_one_base_type_field_struct():
    in_stream = FileWrapper(io.StringIO('struct S {int x;}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 1
    assert p.struct_defs[0].struct_name.lexeme == 'S'
    assert len(p.struct_defs[0].fields) == 1
    assert p.struct_defs[0].fields[0].data_type.is_array == False
    assert p.struct_defs[0].fields[0].data_type.type_name.lexeme == 'int'
    assert p.struct_defs[0].fields[0].var_name.lexeme == 'x'

def test_one_id_field_struct():
    in_stream = FileWrapper(io.StringIO('struct S {S s1;}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 1
    assert p.struct_defs[0].struct_name.lexeme == 'S'
    assert len(p.struct_defs[0].fields) == 1
    assert p.struct_defs[0].fields[0].data_type.is_array == False
    assert p.struct_defs[0].fields[0].data_type.type_name.lexeme == 'S'
    assert p.struct_defs[0].fields[0].var_name.lexeme == 's1'

def test_one_array_field_struct():
    in_stream = FileWrapper(io.StringIO('struct S {array int x1;}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 1
    assert p.struct_defs[0].struct_name.lexeme == 'S'
    assert len(p.struct_defs[0].fields) == 1
    assert p.struct_defs[0].fields[0].data_type.is_array == True
    assert p.struct_defs[0].fields[0].data_type.type_name.lexeme == 'int'
    assert p.struct_defs[0].fields[0].var_name.lexeme == 'x1'

def test_two_field_struct():
    in_stream = FileWrapper(io.StringIO('struct S {int x1; bool x2;}'))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 1
    assert p.struct_defs[0].struct_name.lexeme == 'S'
    assert len(p.struct_defs[0].fields) == 2
    assert p.struct_defs[0].fields[0].data_type.is_array == False
    assert p.struct_defs[0].fields[0].data_type.type_name.lexeme == 'int'
    assert p.struct_defs[0].fields[0].var_name.lexeme == 'x1'
    assert p.struct_defs[0].fields[1].data_type.is_array == False
    assert p.struct_defs[0].fields[1].data_type.type_name.lexeme == 'bool'
    assert p.struct_defs[0].fields[1].var_name.lexeme == 'x2'

def test_three_field_struct():
    in_stream = FileWrapper(io.StringIO(
        'struct S {int x1; bool x2; array S x3;}'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 1
    assert p.struct_defs[0].struct_name.lexeme == 'S'
    assert len(p.struct_defs[0].fields) == 3
    assert p.struct_defs[0].fields[0].data_type.is_array == False
    assert p.struct_defs[0].fields[0].data_type.type_name.lexeme == 'int'
    assert p.struct_defs[0].fields[0].var_name.lexeme == 'x1'
    assert p.struct_defs[0].fields[1].data_type.is_array == False
    assert p.struct_defs[0].fields[1].data_type.type_name.lexeme == 'bool'
    assert p.struct_defs[0].fields[1].var_name.lexeme == 'x2'
    assert p.struct_defs[0].fields[2].data_type.is_array == True
    assert p.struct_defs[0].fields[2].data_type.type_name.lexeme == 'S'
    assert p.struct_defs[0].fields[2].var_name.lexeme == 'x3'

def test_empty_struct_and_fun():
    in_stream = FileWrapper(io.StringIO(
        'struct S1 {} \n'
        'int f() {} \n'
        'struct S2 {} \n'
        'int g() {} \n'
        'struct S3 {} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 2
    assert len(p.struct_defs) == 3
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert p.fun_defs[1].fun_name.lexeme == 'g'
    assert p.struct_defs[0].struct_name.lexeme == 'S1'
    assert p.struct_defs[1].struct_name.lexeme == 'S2'    
    assert p.struct_defs[2].struct_name.lexeme == 'S3'    

    
#----------------------------------------------------------------------
# Variable Declaration Statements
#----------------------------------------------------------------------

def test_var_base_type_var_decls():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1; \n'
        '  double x2; \n'
        '  bool x3; \n'
        '  string x4; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 4
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_array == False
    assert p.fun_defs[0].stmts[1].var_def.data_type.is_array == False
    assert p.fun_defs[0].stmts[2].var_def.data_type.is_array == False
    assert p.fun_defs[0].stmts[3].var_def.data_type.is_array == False    
    assert p.fun_defs[0].stmts[0].var_def.data_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].stmts[1].var_def.data_type.type_name.lexeme == 'double'
    assert p.fun_defs[0].stmts[2].var_def.data_type.type_name.lexeme == 'bool'
    assert p.fun_defs[0].stmts[3].var_def.data_type.type_name.lexeme == 'string'
    assert p.fun_defs[0].stmts[0].var_def.var_name.lexeme == 'x1'
    assert p.fun_defs[0].stmts[1].var_def.var_name.lexeme == 'x2'
    assert p.fun_defs[0].stmts[2].var_def.var_name.lexeme == 'x3'
    assert p.fun_defs[0].stmts[3].var_def.var_name.lexeme == 'x4'

def test_array_var_decl():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array int x1; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_array == True
    assert p.fun_defs[0].stmts[0].var_def.data_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].stmts[0].var_def.var_name.lexeme == 'x1'    

def test_id_var_decl():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  S s1; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_array == False
    assert p.fun_defs[0].stmts[0].var_def.data_type.type_name.lexeme == 'S'
    assert p.fun_defs[0].stmts[0].var_def.var_name.lexeme == 's1'    
    

def test_base_type_var_def():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  int x1 = 0; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_array == False
    assert p.fun_defs[0].stmts[0].var_def.data_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].stmts[0].var_def.var_name.lexeme == 'x1'
    print(p.fun_defs[0].stmts[0].expr)
    assert p.fun_defs[0].stmts[0].expr.not_op == False
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.value.lexeme == '0'

def test_id_var_def():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  Node my_node = null; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_array == False
    assert p.fun_defs[0].stmts[0].var_def.data_type.type_name.lexeme == 'Node'
    assert p.fun_defs[0].stmts[0].var_def.var_name.lexeme == 'my_node'
    assert p.fun_defs[0].stmts[0].expr.not_op == False
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.value.lexeme == 'null'
    
def test_array_var_def():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  array bool my_bools = null; \n'
        '  array Node my_nodes = null; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 2
    assert p.fun_defs[0].stmts[0].var_def.data_type.is_array == True
    assert p.fun_defs[0].stmts[0].var_def.data_type.type_name.lexeme == 'bool'
    assert p.fun_defs[0].stmts[0].var_def.var_name.lexeme == 'my_bools'
    assert p.fun_defs[0].stmts[0].expr.not_op == False
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.value.lexeme == 'null'
    assert p.fun_defs[0].stmts[1].var_def.data_type.is_array == True
    assert p.fun_defs[0].stmts[1].var_def.data_type.type_name.lexeme == 'Node'
    assert p.fun_defs[0].stmts[1].var_def.var_name.lexeme == 'my_nodes'
    assert p.fun_defs[0].stmts[1].expr.not_op == False
    assert p.fun_defs[0].stmts[1].expr.first.rvalue.value.lexeme == 'null'

    
#----------------------------------------------------------------------
# Assignment Statements
#----------------------------------------------------------------------

def test_simple_assignment():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = null; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].lvalue[0].var_name.lexeme == 'x'
    assert p.fun_defs[0].stmts[0].lvalue[0].array_expr == None
    assert p.fun_defs[0].stmts[0].expr.not_op == False
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.value.lexeme == 'null'
    assert p.fun_defs[0].stmts[0].expr.rest == None

def test_simple_path_assignment():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x.y = null; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].lvalue[0].var_name.lexeme == 'x'
    assert p.fun_defs[0].stmts[0].lvalue[0].array_expr == None
    assert p.fun_defs[0].stmts[0].lvalue[1].var_name.lexeme == 'y'
    assert p.fun_defs[0].stmts[0].lvalue[1].array_expr == None
    assert p.fun_defs[0].stmts[0].expr.not_op == False
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.value.lexeme == 'null'
    assert p.fun_defs[0].stmts[0].expr.rest == None

def test_simple_array_assignment():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x[0] = null; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.lvalue[0].var_name.lexeme == 'x'
    assert stmt.lvalue[0].array_expr.not_op == False
    assert stmt.lvalue[0].array_expr.first.rvalue.value.lexeme == '0'
    assert stmt.lvalue[0].array_expr.rest == None
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.value.lexeme == 'null'
    assert stmt.expr.rest == None

def test_multiple_path_assignment():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x1.x2[0].x3.x4[1] = null; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert len(stmt.lvalue) == 4
    assert stmt.lvalue[0].var_name.lexeme == 'x1'
    assert stmt.lvalue[0].array_expr == None
    assert stmt.lvalue[1].var_name.lexeme == 'x2'    
    assert stmt.lvalue[1].array_expr.not_op == False
    assert stmt.lvalue[1].array_expr.first.rvalue.value.lexeme == '0'
    assert stmt.lvalue[2].var_name.lexeme == 'x3'
    assert stmt.lvalue[2].array_expr == None
    assert stmt.lvalue[3].var_name.lexeme == 'x4'
    assert stmt.lvalue[3].array_expr.not_op == False
    assert stmt.lvalue[3].array_expr.first.rvalue.value.lexeme == '1'

    
#----------------------------------------------------------------------
# If Statements
#----------------------------------------------------------------------

def test_single_if_statement():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 0
    assert len(stmt.else_ifs) == 0
    assert len(stmt.else_stmts) == 0
    
def test_if_statement_with_body():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {int x = 0;} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 1
    assert len(stmt.else_ifs) == 0
    assert len(stmt.else_stmts) == 0

def test_if_statement_with_one_else_if():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {} \n'
        '  elseif (false) {} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 0
    assert len(stmt.else_ifs) == 1
    assert stmt.else_ifs[0].condition.first.rvalue.value.lexeme == 'false'
    assert len(stmt.else_ifs[0].stmts) == 0

    
def test_if_statement_with_two_else_ifs():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {} \n'
        '  elseif (false) {} \n'
        '  elseif (true) {} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 0
    assert len(stmt.else_ifs) == 2
    assert stmt.else_ifs[0].condition.first.rvalue.value.lexeme == 'false'
    assert len(stmt.else_ifs[0].stmts) == 0
    assert stmt.else_ifs[1].condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.else_ifs[1].stmts) == 0
    assert len(stmt.else_stmts) == 0

def test_if_statement_with_empty_else():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {} \n'
        '  else {} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 0
    assert len(stmt.else_ifs) == 0
    assert len(stmt.else_stmts) == 0

def test_if_statement_with_non_empty_else():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {} \n'
        '  else {x = 5;} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 0
    assert len(stmt.else_ifs) == 0
    assert len(stmt.else_stmts) == 1

def test_full_if_statement():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {x = 5;} \n'
        '  elseif (false) {x = 6;} \n'
        '  else {x = 7;} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 1
    assert len(stmt.else_ifs) == 1
    assert stmt.else_ifs[0].condition.first.rvalue.value.lexeme == 'false'
    assert len(stmt.else_ifs[0].stmts) == 1
    assert len(stmt.else_stmts) == 1

    
#----------------------------------------------------------------------
# While Statements
#----------------------------------------------------------------------

def test_empty_while_statement():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  while (true) {} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.stmts) == 0

def test_while_statement_with_body():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  while (true) {x = 5;} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.stmts) == 1

    
#----------------------------------------------------------------------
# Expressions
#----------------------------------------------------------------------

def test_literals():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = true; \n'
        '  x = false; \n'        
        '  x = 0; \n'
        '  x = 0.0; \n'
        '  x = "a"; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 5
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.value.lexeme == 'true'
    assert p.fun_defs[0].stmts[1].expr.first.rvalue.value.lexeme == 'false'
    assert p.fun_defs[0].stmts[2].expr.first.rvalue.value.lexeme == '0'    
    assert p.fun_defs[0].stmts[3].expr.first.rvalue.value.lexeme == '0.0'    
    assert p.fun_defs[0].stmts[4].expr.first.rvalue.value.lexeme == 'a'        
    assert p.fun_defs[0].stmts[0].expr.not_op == False
    assert p.fun_defs[0].stmts[1].expr.not_op == False
    assert p.fun_defs[0].stmts[2].expr.not_op == False
    assert p.fun_defs[0].stmts[3].expr.not_op == False
    assert p.fun_defs[0].stmts[4].expr.not_op == False

def test_simple_bool_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = true and false; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.value.lexeme == 'true'
    assert stmt.expr.op.lexeme == 'and'
    assert stmt.expr.rest.not_op == False
    assert stmt.expr.rest.first.rvalue.value.lexeme == 'false'
    assert stmt.expr.rest.op == None
    assert stmt.expr.rest.rest == None

def test_simple_not_bool_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = not true and false; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == True
    assert stmt.expr.first.rvalue.value.lexeme == 'true'
    assert stmt.expr.op.lexeme == 'and'
    assert stmt.expr.rest.not_op == False
    assert stmt.expr.rest.first.rvalue.value.lexeme == 'false'
    assert stmt.expr.rest.op == None
    assert stmt.expr.rest.rest == None    

def test_simple_paren_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = (1 + 2); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.expr.first.rvalue.value.lexeme == '1'
    assert stmt.expr.first.expr.op.lexeme == '+'
    assert stmt.expr.first.expr.rest.not_op == False
    assert stmt.expr.first.expr.rest.first.rvalue.value.lexeme == '2'
    assert stmt.expr.first.expr.rest.op == None
    assert stmt.expr.first.expr.rest.rest == None    

def test_expr_after_paren_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = (1 + 2) - 3; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.expr.first.rvalue.value.lexeme == '1'
    assert stmt.expr.first.expr.op.lexeme == '+'
    assert stmt.expr.first.expr.rest.not_op == False
    assert stmt.expr.first.expr.rest.first.rvalue.value.lexeme == '2'
    assert stmt.expr.first.expr.rest.op == None
    assert stmt.expr.first.expr.rest.rest == None    
    assert stmt.expr.op.lexeme == '-'
    assert stmt.expr.rest.not_op == False
    assert stmt.expr.rest.first.rvalue.value.lexeme == '3'
    assert stmt.expr.rest.op == None
    assert stmt.expr.rest.rest == None

def test_expr_before_paren_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = 3 * (1 + 2); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.value.lexeme == '3'
    assert stmt.expr.op.lexeme == '*'
    assert stmt.expr.rest.not_op == False
    assert stmt.expr.rest.first.expr.first.rvalue.value.lexeme == '1'
    assert stmt.expr.rest.first.expr.op.lexeme == '+'
    assert stmt.expr.rest.first.expr.rest.not_op == False
    assert stmt.expr.rest.first.expr.rest.first.rvalue.value.lexeme == '2'
    assert stmt.expr.rest.first.expr.rest.op == None
    assert stmt.expr.rest.first.expr.rest.rest == None
    assert stmt.expr.rest.op == None
    assert stmt.expr.rest.rest == None

def test_expr_with_two_ops():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = 1 / 2 * 3; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.value.lexeme == '1'
    assert stmt.expr.op.lexeme == '/'
    assert stmt.expr.rest.not_op == False
    assert stmt.expr.rest.first.rvalue.value.lexeme == '2'
    assert stmt.expr.rest.op.lexeme == '*'
    assert stmt.expr.rest.rest.not_op == False
    assert stmt.expr.rest.rest.first.rvalue.value.lexeme == '3'
    assert stmt.expr.rest.rest.op == None
    assert stmt.expr.rest.rest.rest == None    

def test_empty_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  f(); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.fun_name.lexeme == 'f'
    assert len(stmt.args) == 0

def test_one_arg_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  f(3); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.fun_name.lexeme == 'f'
    assert len(stmt.args) == 1
    assert stmt.args[0].not_op == False
    assert stmt.args[0].first.rvalue.value.lexeme == '3'
    assert stmt.args[0].op == None
    assert stmt.args[0].rest == None    

def test_two_arg_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  f(3, 4); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.fun_name.lexeme == 'f'
    assert len(stmt.args) == 2
    assert stmt.args[0].not_op == False
    assert stmt.args[0].first.rvalue.value.lexeme == '3'
    assert stmt.args[0].op == None
    assert stmt.args[0].rest == None    
    assert stmt.args[1].not_op == False
    assert stmt.args[1].first.rvalue.value.lexeme == '4'
    assert stmt.args[1].op == None
    assert stmt.args[1].rest == None    
    
def test_simple_struct_new_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = new S(); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.type_name.lexeme == 'S'
    assert stmt.expr.first.rvalue.array_expr == None
    assert len(stmt.expr.first.rvalue.struct_params) == 0

def test_two_arg_struct_new_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = new S(3, 4); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.type_name.lexeme == 'S'
    assert stmt.expr.first.rvalue.array_expr == None
    assert len(stmt.expr.first.rvalue.struct_params) == 2
    assert stmt.expr.first.rvalue.struct_params[0].first.rvalue.value.lexeme == '3'
    assert stmt.expr.first.rvalue.struct_params[1].first.rvalue.value.lexeme == '4'

def test_base_type_array_new_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = new int[10]; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.type_name.lexeme == 'int'
    assert stmt.expr.first.rvalue.array_expr.first.rvalue.value.lexeme == '10'
    assert stmt.expr.first.rvalue.struct_params == None

def test_simple_var_rvalue():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = y; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert len(stmt.expr.first.rvalue.path) == 1
    assert stmt.expr.first.rvalue.path[0].var_name.lexeme == 'y'
    assert stmt.expr.first.rvalue.path[0].array_expr == None

def test_simple_array_var_rvalue():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = y[0]; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert len(stmt.expr.first.rvalue.path) == 1
    assert stmt.expr.first.rvalue.path[0].var_name.lexeme == 'y'
    assert stmt.expr.first.rvalue.path[0].array_expr.not_op == False
    assert stmt.expr.first.rvalue.path[0].array_expr.first.rvalue.value.lexeme == '0'
    assert stmt.expr.first.rvalue.path[0].array_expr.op == None
    assert stmt.expr.first.rvalue.path[0].array_expr.rest == None

def test_two_path_var_rvalue():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = y.z; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert len(stmt.expr.first.rvalue.path) == 2
    assert stmt.expr.first.rvalue.path[0].var_name.lexeme == 'y'
    assert stmt.expr.first.rvalue.path[0].array_expr == None
    assert stmt.expr.first.rvalue.path[1].var_name.lexeme == 'z'
    assert stmt.expr.first.rvalue.path[1].array_expr == None


def test_mixed_path_var_rvalue():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = u[2].v.w[1].y; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert len(stmt.expr.first.rvalue.path) == 4
    assert stmt.expr.not_op == False
    assert stmt.expr.op == None
    assert stmt.expr.rest == None
    path = stmt.expr.first.rvalue.path
    assert path[0].var_name.lexeme == 'u'
    assert path[0].array_expr.not_op == False
    assert path[0].array_expr.first.rvalue.value.lexeme == '2'
    assert path[0].array_expr.op == None
    assert path[0].array_expr.rest == None
    assert path[1].var_name.lexeme == 'v'
    assert path[1].array_expr == None
    assert path[2].var_name.lexeme == 'w'
    assert path[2].array_expr.not_op == False
    assert path[2].array_expr.first.rvalue.value.lexeme == '1'
    assert path[2].array_expr.op == None
    assert path[2].array_expr.rest == None
    assert path[3].var_name.lexeme == 'y'
    assert path[3].array_expr == None


#----------------------------------------------------------------------
# TODO: Add at least 10 of your own tests below. Define at least two
# tests for statements, one test for return statements, five tests
# for expressions, and two tests that are more involved combining
# multiple constructs.
#----------------------------------------------------------------------

# Two for statement tests

def test_empty_for_statement():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  for (int i = 0; i < 5; i = i + 1) {}\n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.var_decl.var_def.data_type.is_array == False
    assert stmt.var_decl.var_def.data_type.type_name.lexeme == 'int'
    assert stmt.var_decl.var_def.var_name.lexeme == 'i'
    assert stmt.var_decl.expr.not_op == False
    assert stmt.var_decl.expr.first.rvalue.value.lexeme == '0'
    assert stmt.var_decl.expr.not_op == False
    assert stmt.condition.first.rvalue.path[0].var_name.lexeme == 'i'
    assert stmt.condition.op.lexeme == '<'
    assert stmt.condition.rest.not_op == False
    assert stmt.condition.rest.first.rvalue.value.lexeme == '5'
    assert stmt.condition.rest.op == None
    assert stmt.condition.rest.rest == None
    assert stmt.assign_stmt.lvalue[0].var_name.lexeme == 'i'
    assert stmt.assign_stmt.lvalue[0].array_expr == None
    assert stmt.assign_stmt.expr.not_op == False
    assert stmt.assign_stmt.expr.first.rvalue.path[0].var_name.lexeme == 'i'
    assert stmt.assign_stmt.expr.op.lexeme == '+'
    assert stmt.assign_stmt.expr.rest.not_op == False
    assert stmt.assign_stmt.expr.rest.first.rvalue.value.lexeme == '1'

def test_for_statement():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  for (int i = 0; i < 5; i = i + 1) {\n'
        '      x = 5; \n'
        '  }'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.var_decl.var_def.data_type.is_array == False
    assert stmt.var_decl.var_def.data_type.type_name.lexeme == 'int'
    assert stmt.var_decl.var_def.var_name.lexeme == 'i'
    assert stmt.var_decl.expr.not_op == False
    assert stmt.var_decl.expr.first.rvalue.value.lexeme == '0'
    assert stmt.var_decl.expr.not_op == False
    assert stmt.condition.first.rvalue.path[0].var_name.lexeme == 'i'
    assert stmt.condition.op.lexeme == '<'
    assert stmt.condition.rest.not_op == False
    assert stmt.condition.rest.first.rvalue.value.lexeme == '5'
    assert stmt.condition.rest.op == None
    assert stmt.condition.rest.rest == None
    assert stmt.assign_stmt.lvalue[0].var_name.lexeme == 'i'
    assert stmt.assign_stmt.lvalue[0].array_expr == None
    assert stmt.assign_stmt.expr.not_op == False
    assert stmt.assign_stmt.expr.first.rvalue.path[0].var_name.lexeme == 'i'
    assert stmt.assign_stmt.expr.op.lexeme == '+'
    assert stmt.assign_stmt.expr.rest.not_op == False
    assert stmt.assign_stmt.expr.rest.first.rvalue.value.lexeme == '1'
    assert stmt.assign_stmt.expr.rest.op == None
    assert stmt.assign_stmt.expr.rest.rest == None
    assert stmt.stmts[0].lvalue[0].var_name.lexeme == 'x'
    assert stmt.stmts[0].lvalue[0].array_expr == None
    assert stmt.stmts[0].expr.first.rvalue.value.lexeme == '5'

# One return statement test
def test_return():
    in_stream = FileWrapper(io.StringIO(
        'int f() { \n'
        '   return 3; \n'
        '}'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 1
    assert len(p.struct_defs) == 0
    assert p.fun_defs[0].return_type.type_name.lexeme == 'int'
    assert p.fun_defs[0].return_type.is_array == False
    assert p.fun_defs[0].fun_name.lexeme == 'f'
    assert len(p.fun_defs[0].params) == 0
    assert len(p.fun_defs[0].stmts) == 1
    assert p.fun_defs[0].stmts[0].expr.not_op == False
    assert p.fun_defs[0].stmts[0].expr.first.rvalue.value.lexeme == '3' 
    assert p.fun_defs[0].stmts[0].expr.op == None
    assert p.fun_defs[0].stmts[0].expr.rest == None


# Five expression tests

def test_long_paren_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = (1 + 2 * 3 - 5); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.expr.first.rvalue.value.lexeme == '1'
    assert stmt.expr.first.expr.op.lexeme == '+'
    assert stmt.expr.first.expr.rest.not_op == False
    assert stmt.expr.first.expr.rest.first.rvalue.value.lexeme == '2'
    assert stmt.expr.first.expr.rest.op.lexeme == '*'
    assert stmt.expr.first.expr.rest.not_op == False
    assert stmt.expr.first.expr.rest.rest.first.rvalue.value.lexeme == '3'
    assert stmt.expr.first.expr.rest.rest.op.lexeme == '-'
    assert stmt.expr.first.expr.rest.not_op == False
    assert stmt.expr.first.expr.rest.rest.rest.first.rvalue.value.lexeme == '5'

def test_long_expr_after_paren_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  x = (3 - 1) - x + y; \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.expr.first.rvalue.value.lexeme == '3'
    assert stmt.expr.first.expr.op.lexeme == '-'
    assert stmt.expr.first.expr.rest.not_op == False
    assert stmt.expr.first.expr.rest.first.rvalue.value.lexeme == '1'
    assert stmt.expr.first.expr.rest.op == None
    assert stmt.expr.first.expr.rest.rest == None    
    assert stmt.expr.op.lexeme == '-'
    assert stmt.expr.rest.not_op == False
    assert stmt.expr.rest.first.rvalue.path[0].var_name.lexeme == 'x'
    assert stmt.expr.rest.op.lexeme == '+'
    assert stmt.expr.rest.not_op == False
    assert stmt.expr.rest.rest.first.rvalue.path[0].var_name.lexeme == 'y'

def test_three_arg_struct_new_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  y = new T(2, 14, 7); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.expr.not_op == False
    assert stmt.expr.first.rvalue.type_name.lexeme == 'T'
    assert stmt.expr.first.rvalue.array_expr == None
    assert len(stmt.expr.first.rvalue.struct_params) == 3
    assert stmt.expr.first.rvalue.struct_params[0].first.rvalue.value.lexeme == '2'
    assert stmt.expr.first.rvalue.struct_params[1].first.rvalue.value.lexeme == '14'
    assert stmt.expr.first.rvalue.struct_params[2].first.rvalue.value.lexeme == '7'

def test_two_empty_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  f(); \n'
        '  C(); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 2
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.fun_name.lexeme == 'f'
    assert len(stmt.args) == 0
    stmt = p.fun_defs[0].stmts[1]
    assert stmt.fun_name.lexeme == 'C'
    assert len(stmt.args) == 0

def test_5_arg_call_expr():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  print (1, 2, 3, 4, 5); \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.fun_name.lexeme == 'print'
    assert len(stmt.args) == 5
    assert stmt.args[0].not_op == False
    assert stmt.args[0].first.rvalue.value.lexeme == '1'
    assert stmt.args[0].op == None
    assert stmt.args[0].rest == None    
    assert stmt.args[1].not_op == False
    assert stmt.args[1].first.rvalue.value.lexeme == '2'
    assert stmt.args[1].op == None
    assert stmt.args[1].rest == None  
    assert stmt.args[2].not_op == False
    assert stmt.args[2].first.rvalue.value.lexeme == '3'
    assert stmt.args[2].op == None
    assert stmt.args[2].rest == None    
    assert stmt.args[3].not_op == False
    assert stmt.args[3].first.rvalue.value.lexeme == '4'
    assert stmt.args[3].op == None
    assert stmt.args[3].rest == None    
    assert stmt.args[4].not_op == False
    assert stmt.args[4].first.rvalue.value.lexeme == '5'
    assert stmt.args[4].op == None
    assert stmt.args[4].rest == None      

# Three multiple constructs
def test_while_statement_with_if():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  while (true) { \n'
        '      if (true) { \n'
        '          x = 5; \n'
        '      } \n'
        '  }'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.stmts) == 1
    stmt = p.fun_defs[0].stmts[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 1
    assert len(stmt.else_ifs) == 0
    assert len(stmt.else_stmts) == 0

def test_while_statement_with_if_and_elif():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  while (true) { \n'
        '      if (true) { \n'
        '          x = 5; \n'
        '      } \n'
        '      elseif (false) { \n'
        '          x = 1;'
        '      }'
        '  }'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.stmts) == 1
    stmt = p.fun_defs[0].stmts[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 1
    assert len(stmt.else_ifs) == 1
    assert stmt.else_ifs[0].condition.first.rvalue.value.lexeme == 'false'
    assert len(stmt.else_ifs[0].stmts) == 1
    assert len(stmt.else_stmts) == 0

def test_for_nest_statement():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  for (int i = 0; i < 5; i = i + 1) {\n'
        '      if(true) {} \n'
        '  } \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.var_decl.var_def.data_type.is_array == False
    assert stmt.var_decl.var_def.data_type.type_name.lexeme == 'int'
    assert stmt.var_decl.var_def.var_name.lexeme == 'i'
    assert stmt.var_decl.expr.not_op == False
    assert stmt.var_decl.expr.first.rvalue.value.lexeme == '0'
    assert stmt.var_decl.expr.not_op == False
    assert stmt.condition.first.rvalue.path[0].var_name.lexeme == 'i'
    assert stmt.condition.op.lexeme == '<'
    assert stmt.condition.rest.not_op == False
    assert stmt.condition.rest.first.rvalue.value.lexeme == '5'
    assert stmt.condition.rest.op == None
    assert stmt.condition.rest.rest == None
    assert stmt.assign_stmt.lvalue[0].var_name.lexeme == 'i'
    assert stmt.assign_stmt.lvalue[0].array_expr == None
    assert stmt.assign_stmt.expr.not_op == False
    assert stmt.assign_stmt.expr.first.rvalue.path[0].var_name.lexeme == 'i'
    assert stmt.assign_stmt.expr.op.lexeme == '+'
    assert stmt.assign_stmt.expr.rest.not_op == False
    assert stmt.assign_stmt.expr.rest.first.rvalue.value.lexeme == '1'
    assert stmt.assign_stmt.expr.rest.op == None
    assert stmt.assign_stmt.expr.rest.rest == None
    stmt = p.fun_defs[0].stmts[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 0
    assert len(stmt.else_ifs) == 0
    assert len(stmt.else_stmts) == 0

def test_try_statement():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  try {       \n'
        '    int result = 0; \n'
        '  }             \n'   
        '  catch { print("ERROR"); } \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert len(stmt.try_part) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert len(stmt.catch_parts) == 1
