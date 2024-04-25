"""Unit tests for CPSC 326 HW-1. 

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



#----------------------------------------------------------------------
# Positive Test Cases
#----------------------------------------------------------------------

def test_simple_symbol():
    in_stream = FileWrapper(io.StringIO('.'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.DOT
    assert t.lexeme == '.'
    assert t.line == 1
    assert t.column == 1

    
def test_empty_input():
    in_stream = FileWrapper(io.StringIO(''))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.EOS
    assert t.lexeme == ''
    assert t.line == 1
    assert t.column == 1

    
def test_symbol_then_eof():
    in_stream = FileWrapper(io.StringIO(';'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.SEMICOLON
    assert t.lexeme == ';'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.EOS
    assert t.lexeme == ''
    assert t.line == 1
    assert t.column == 2

    
def test_single_comment():
    in_stream = FileWrapper(io.StringIO('// a comment'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.COMMENT
    assert t.lexeme == ' a comment'
    assert t.line == 1
    assert t.column == 1

    
def test_two_comments():
    m = ('// first comment\n'
         ' // second comment')
    in_stream = FileWrapper(io.StringIO(m))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.COMMENT
    assert t.lexeme == ' first comment'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.COMMENT
    assert t.lexeme == ' second comment'
    assert t.line == 2
    assert t.column == 2

    
def test_one_character_symbols():
    in_stream = FileWrapper(io.StringIO(',.;+-*/()[]{}=<>'))
    l = Lexer(in_stream)
    types = [TokenType.COMMA, TokenType.DOT, TokenType.SEMICOLON, TokenType.PLUS,
             TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE, TokenType.LPAREN,
             TokenType.RPAREN, TokenType.LBRACKET, TokenType.RBRACKET,
             TokenType.LBRACE, TokenType.RBRACE, TokenType.ASSIGN,
             TokenType.LESS, TokenType.GREATER]
    for i in range(len(types)):
        t = l.next_token()
        assert t.token_type == types[i]
        assert t.line == 1
        assert t.column == i + 1
    assert l.next_token().token_type == TokenType.EOS


def test_two_character_symbols():
    in_stream = FileWrapper(io.StringIO('!=>=<==='))
    l = Lexer(in_stream)
    types = [TokenType.NOT_EQUAL, TokenType.GREATER_EQ, TokenType.LESS_EQ,
             TokenType.EQUAL]
    for i in range(len(types)):
        t = l.next_token()
        assert t.token_type == types[i]
        assert t.line == 1
        assert t.column == (i * 2) + 1
    assert l.next_token().token_type == TokenType.EOS


def test_one_symbol_per_line():
    in_stream = FileWrapper(io.StringIO(',\n.\n;\n('))    
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.COMMA
    assert t.lexeme == ','
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.DOT
    assert t.lexeme == '.'
    assert t.line == 2
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.SEMICOLON
    assert t.lexeme == ';'
    assert t.line == 3
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.LPAREN
    assert t.lexeme == '('
    assert t.line == 4
    assert t.column == 1
    assert l.next_token().token_type == TokenType.EOS


def test_one_char_strings():
    in_stream = FileWrapper(io.StringIO('"a" "?" "<"'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.STRING_VAL
    assert t.lexeme == 'a'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.STRING_VAL
    assert t.lexeme == '?'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()
    assert t.token_type == TokenType.STRING_VAL
    assert t.lexeme == '<'
    assert t.line == 1
    assert t.column == 9
    assert l.next_token().token_type == TokenType.EOS


def test_multi_char_strings():
    in_stream = FileWrapper(io.StringIO('"abc" "><!=" "foo bar baz"'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.STRING_VAL
    assert t.lexeme == 'abc'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.STRING_VAL
    assert t.lexeme == '><!='
    assert t.line == 1
    assert t.column == 7
    t = l.next_token()
    assert t.token_type == TokenType.STRING_VAL
    assert t.lexeme == 'foo bar baz'
    assert t.line == 1
    assert t.column == 14
    assert l.next_token().token_type == TokenType.EOS


def test_basic_ints():
    in_stream = FileWrapper(io.StringIO('0 42 10 9876543210'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '0'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '42'
    assert t.line == 1
    assert t.column == 3
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '10'
    assert t.line == 1
    assert t.column == 6
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '9876543210'
    assert t.line == 1
    assert t.column == 9
    assert l.next_token().token_type == TokenType.EOS


def test_basic_doubles():
    in_stream = FileWrapper(io.StringIO('0.0 0.00 3.14 321.123'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '0.0'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '0.00'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '3.14'
    assert t.line == 1
    assert t.column == 10
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '321.123'
    assert t.line == 1
    assert t.column == 15
    assert l.next_token().token_type == TokenType.EOS

    
def test_special_values():
    in_stream = FileWrapper(io.StringIO('null true false'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.NULL_VAL
    assert t.lexeme == 'null'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.BOOL_VAL
    assert t.lexeme == 'true'
    assert t.line == 1
    assert t.column == 6
    t = l.next_token()    
    assert t.token_type == TokenType.BOOL_VAL
    assert t.lexeme == 'false'
    assert t.line == 1
    assert t.column == 11
    assert l.next_token().token_type == TokenType.EOS    

    
def test_primitive_types():
    in_stream = FileWrapper(io.StringIO('int double string bool void'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.INT_TYPE
    assert t.lexeme == 'int'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_TYPE
    assert t.lexeme == 'double'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()    
    assert t.token_type == TokenType.STRING_TYPE
    assert t.lexeme == 'string'
    assert t.line == 1
    assert t.column == 12
    t = l.next_token()    
    assert t.token_type == TokenType.BOOL_TYPE
    assert t.lexeme == 'bool'
    assert t.line == 1
    assert t.column == 19
    t = l.next_token()    
    assert t.token_type == TokenType.VOID_TYPE
    assert t.lexeme == 'void'
    assert t.line == 1
    assert t.column == 24
    assert l.next_token().token_type == TokenType.EOS    

    
def test_logical_operators():
    in_stream = FileWrapper(io.StringIO('and or not'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.AND
    assert t.lexeme == 'and'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.OR
    assert t.lexeme == 'or'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()
    assert t.token_type == TokenType.NOT
    assert t.lexeme == 'not'
    assert t.line == 1
    assert t.column == 8
    assert l.next_token().token_type == TokenType.EOS    


def test_if_statement_reserved_words():
    in_stream = FileWrapper(io.StringIO('if elseif else'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.IF
    assert t.lexeme == 'if'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.ELSEIF
    assert t.lexeme == 'elseif'
    assert t.line == 1
    assert t.column == 4
    t = l.next_token()
    assert t.token_type == TokenType.ELSE
    assert t.lexeme == 'else'
    assert t.line == 1
    assert t.column == 11
    assert l.next_token().token_type == TokenType.EOS    


def test_try_catch_reserved_words():
    in_stream = FileWrapper(io.StringIO('try catch'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.TRY
    assert t.lexeme == 'try'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.CATCH
    assert t.lexeme == 'catch'
    assert t.line == 1
    assert t.column == 5
    assert l.next_token().token_type == TokenType.EOS    

def test_try_catch_more_reserved_words():
    in_stream = FileWrapper(io.StringIO('as ZeroDivError'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.AS
    assert t.lexeme == 'as'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.ZERODIV
    assert t.lexeme == 'ZeroDivError'
    assert t.line == 1
    assert t.column == 4
    assert l.next_token().token_type == TokenType.EOS    

def test_loop_statement_reserved_words():
    in_stream = FileWrapper(io.StringIO('while for'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.WHILE
    assert t.lexeme == 'while'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.FOR
    assert t.lexeme == 'for'
    assert t.line == 1
    assert t.column == 7
    assert l.next_token().token_type == TokenType.EOS    

    
def test_function_and_complex_type_reserved_words():
    in_stream = FileWrapper(io.StringIO('return struct array new'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.RETURN
    assert t.lexeme == 'return'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.STRUCT
    assert t.lexeme == 'struct'
    assert t.line == 1
    assert t.column == 8
    t = l.next_token()
    assert t.token_type == TokenType.ARRAY
    assert t.lexeme == 'array'
    assert t.line == 1
    assert t.column == 15
    t = l.next_token()
    assert t.token_type == TokenType.NEW
    assert t.lexeme == 'new'
    assert t.line == 1
    assert t.column == 21
    assert l.next_token().token_type == TokenType.EOS    


def test_basic_identifiers():
    in_stream = FileWrapper(io.StringIO('x xs f0_0 foo_bar foo_bar_baz quix__'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'x'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'xs'
    assert t.line == 1
    assert t.column == 3
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'f0_0'
    assert t.line == 1
    assert t.column == 6
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'foo_bar'
    assert t.line == 1
    assert t.column == 11
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'foo_bar_baz'
    assert t.line == 1
    assert t.column == 19
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'quix__'
    assert t.line == 1
    assert t.column == 31
    assert l.next_token().token_type == TokenType.EOS    
    

def test_with_comments():
    in_stream = FileWrapper(io.StringIO('x < 1 // test 1\nif 3.14'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'x'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.LESS
    assert t.lexeme == '<'
    assert t.line == 1
    assert t.column == 3
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '1'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()
    assert t.token_type == TokenType.COMMENT
    assert t.lexeme == ' test 1'
    assert t.line == 1
    assert t.column == 7
    t = l.next_token()
    assert t.token_type == TokenType.IF
    assert t.lexeme == 'if'
    assert t.line == 2
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '3.14'
    assert t.line == 2
    assert t.column == 4
    assert l.next_token().token_type == TokenType.EOS    

    
def test_no_spaces_tokens():
    in_stream = FileWrapper(io.StringIO('for(int x)ify=4;'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.FOR
    assert t.lexeme == 'for'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.LPAREN
    assert t.lexeme == '('
    assert t.line == 1
    assert t.column == 4
    t = l.next_token()
    assert t.token_type == TokenType.INT_TYPE
    assert t.lexeme == 'int'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'x'
    assert t.line == 1
    assert t.column == 9
    t = l.next_token()
    assert t.token_type == TokenType.RPAREN
    assert t.lexeme == ')'
    assert t.line == 1
    assert t.column == 10
    t = l.next_token()
    assert t.token_type == TokenType.ID
    assert t.lexeme == 'ify'
    assert t.line == 1
    assert t.column == 11
    t = l.next_token()
    assert t.token_type == TokenType.ASSIGN
    assert t.lexeme == '='
    assert t.line == 1
    assert t.column == 14
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '4'
    assert t.line == 1
    assert t.column == 15
    t = l.next_token()
    assert t.token_type == TokenType.SEMICOLON
    assert t.lexeme == ';'
    assert t.line == 1
    assert t.column == 16
    assert l.next_token().token_type == TokenType.EOS        

    
def test_no_spaces_numbers():
    in_stream = FileWrapper(io.StringIO('32.1.42 .0.0'))
    l = Lexer(in_stream)
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '32.1'
    assert t.line == 1
    assert t.column == 1
    t = l.next_token()
    assert t.token_type == TokenType.DOT
    assert t.lexeme == '.'
    assert t.line == 1
    assert t.column == 5
    t = l.next_token()
    assert t.token_type == TokenType.INT_VAL
    assert t.lexeme == '42'
    assert t.line == 1
    assert t.column == 6
    t = l.next_token()
    assert t.token_type == TokenType.DOT
    assert t.lexeme == '.'
    assert t.line == 1
    assert t.column == 9
    t = l.next_token()
    assert t.token_type == TokenType.DOUBLE_VAL
    assert t.lexeme == '0.0'
    assert t.line == 1
    assert t.column == 10
    assert l.next_token().token_type == TokenType.EOS        


#------------------------------------------------------------
# Negative Test Cases
#------------------------------------------------------------
    
def test_non_terminated_string():
    in_stream = FileWrapper(io.StringIO('"hello \nworld"'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')

    
def test_invalid_not():
    in_stream = FileWrapper(io.StringIO('!>'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')
    in_stream = FileWrapper(io.StringIO('!'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')

    
def test_missing_double_digit():
    in_stream = FileWrapper(io.StringIO('32.a'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')

    
def test_leading_zero():
    in_stream = FileWrapper(io.StringIO('02'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')
    in_stream = FileWrapper(io.StringIO('02.1'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')


def test_invalid_symbol():
    # note: there are more illegal symbols than these two
    in_stream = FileWrapper(io.StringIO('#'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')
    in_stream = FileWrapper(io.StringIO('?'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')

    
def test_invalid_id():
    # note: there are more illegal symbols than these two
    in_stream = FileWrapper(io.StringIO('_xs'))
    l = Lexer(in_stream)
    with pytest.raises(MyPLError) as e:
        l.next_token()
    assert str(e.value).startswith('Lexer Error')
