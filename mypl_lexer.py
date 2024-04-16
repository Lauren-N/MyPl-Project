"""The MyPL Lexer class.

NAME: Lauren Nguyen
DATE: Spring 2024
CLASS: CPSC 326

"""

from mypl_token import *
from mypl_error import *
import re


class Lexer:
    """For obtaining a token stream from a program."""

    def __init__(self, in_stream):
        """Create a Lexer over the given input stream.

        Args:
            in_stream -- The input stream. 

        """
        self.in_stream = in_stream
        self.line = 1
        self.column = 0


    def read(self):
        """Returns and removes one character from the input stream."""
        self.column += 1
        return self.in_stream.read_char()

    
    def peek(self):
        """Returns but doesn't remove one character from the input stream."""
        return self.in_stream.peek_char()

    
    def eof(self, ch):
        """Return true if end-of-file character"""
        return ch == ''

    
    def error(self, message, line, column):
        raise LexerError(f'{message} at line {line}, column {column}')

    
    def next_token(self):
        """Return the next token in the lexer's input stream."""
        # read initial character
        ch = self.read()

        col_start = self.column
        line_start = self.line

        # DICT to hold all one char symbols
        one_char_symbols = {
            '.' : TokenType.DOT,
            ',' : TokenType.COMMA,
            '(' : TokenType.LPAREN,
            ')' : TokenType.RPAREN,
            '{' : TokenType.LBRACE,
            '}' : TokenType.RBRACE,
            ';' : TokenType.SEMICOLON,
            '[' : TokenType.LBRACKET,
            ']' : TokenType.RBRACKET,
            '*' : TokenType.TIMES,
            '/' : TokenType.DIVIDE,
            '+' : TokenType.PLUS,
            '-' : TokenType.MINUS,
            '=' : TokenType.ASSIGN,
            '<' : TokenType.LESS,
            '>' : TokenType.GREATER,
        }

        # DICT to hold all single digit numbers
        single_digits = {
            '0': TokenType.INT_VAL,
            '1': TokenType.INT_VAL,
            '2': TokenType.INT_VAL,
            '3': TokenType.INT_VAL,
            '4': TokenType.INT_VAL,
            '5': TokenType.INT_VAL,
            '6': TokenType.INT_VAL,
            '7': TokenType.INT_VAL,
            '8': TokenType.INT_VAL,
            '9': TokenType.INT_VAL
        }

        # WHITESPACE
        if(ch.isspace()):
            while((ch.isspace()) and (self.eof(ch) == False)): # while there is space and it is not the end of file
                if(ch == '\n'):
                    ch = self.read() # read new line char
                    self.column = 1 # reset cols
                    self.line +=1 # add to line
                if(ch.isspace()):
                    ch = self.read()

        # EOF
        if(self.eof(ch)):
            return Token(TokenType.EOS, "", self.line, self.column)

        # COMMENTS
        if ch == '/' and self.peek() == '/': # looking for // in ch and the next character
            col_start = self.column # saving start column and line
            line_start = self.line
            lex = '' # string to hold lexeme
            ch = self.read() # reading past the "//" characters
            ch = self.read()

            while (ch != '\n'): # since comments can not be multi line, while the ch be analyzed is not "\n" enter loop
                if(self.eof(ch)): # if it is the end of file return as a comment
                    return Token(TokenType.COMMENT, lex, line_start, col_start)
                lex += ch # building lexeme
                ch = self.read() # reading next character
            if(ch == "\n"): # if the character is now "\n" enter
                self.line = self.line + 1 # add to the line
                self.column = 0 # reset cols
            return Token(TokenType.COMMENT, lex, line_start, col_start) # return built up lexeme


        # NOT EQUAL
        if(ch == '!'):
            if(self.peek() == '='):
                start_col = self.column
                ch = self.read()
                self.column-=1
                return Token(TokenType.NOT_EQUAL, '!=', self.line, start_col)

        # GREATER THAN EQUAL
        if(ch == '>'):
            if(self.peek() == '='):
                ch = self.read()
                # self.column-=1
                return Token(TokenType.GREATER_EQ, '>=', self.line, self.column)

        # LESS THAN EQUAL
        if(ch == '<'):
            if(self.peek() == '='):
                ch = self.read()
                # self.column-=1
                return Token(TokenType.LESS_EQ, '<=', self.line, self.column)

        # EQUAL
        if(ch == '='):
            if(self.peek() == '='):
                ch = self.read()
                # self.column-=1
                return Token(TokenType.EQUAL, '==', self.line, self.column)
    
        # STRINGS
        if(ch == '"'): # strings all start with '"" so enter this conditional if it is a string
            lex = '' # string to hold lexeme
            start_col = self.column # saving column and line states
            line_start = self.line
            ch = self.read() # reading past the double quotes
            while(ch != '"'):
                if (ch == '\n') or (self.eof(ch)): # error checking for a non terminated string
                    self.error("Non Terminated String", line_start, start_col)
                lex += ch # building lexeme
                ch = self.read() # read next char
            return Token(TokenType.STRING_VAL, lex, self.line, start_col) # return lexeme

        # ONE CHARACTER SYMBOLS
        if(ch in one_char_symbols): # if ch is in the one_char_symbol dict enter condiitonal
            start_line = self.line # save line state
            return Token(one_char_symbols[ch], ch, start_line, self.column) # return the symbol

        # INTS & DOUBLES
        if(ch.isdigit()):
            dot = 0 # creating a variable to keep track of dots seen to ensure correct double syntax
            start_col = self.column # saving column state
            lex = '' # variable to hold lexeme
            lex += ch # adding first charcater to lexeme
            next_num = self.peek() # creating a variable to peek ahead to ensure proper number builds

            if((ch == '0') and (next_num.isdecimal())): # error checking for leading zeros
                self.error("Leading zero", self.line, start_col)

            while((next_num.isdecimal()) or (next_num == '.') and (dot < 1)): # while the next number is a decimal OR if the look ahead variable sees a dot AND the dot counter is not above 1
                if(next_num == '.'): # starting to create the double if we see that a dot is ahead
                    dot+=1 # add to the dot counter
                    ch = self.read() # reading forward to the dot
                    if(self.peek().isdecimal() == False): # if the number ahead is a decimal, invalid syntax and return an error
                        self.error("Invalid syntax", self.line, col_start)
                else: 
                    ch = self.read() # if not then read ahead to the next character
                lex += ch # building the lexeme
                next_num = self.peek() # moving our look ahead variable to the next position in the string

            if '.' in lex: # if there is a dot present return as a double
                return Token(TokenType.DOUBLE_VAL, lex, self.line, start_col)
            else: # if not then return as a integer
                return Token(TokenType.INT_VAL, lex, self.line, start_col)
            
        # RESERVED WORDS
        if(ch.isalpha()):
            start_col = self.column # saving column state
            lex = '' # lexeme
            lex += ch # starting to build the lexeme by adding the first char

            while((self.peek().isalpha()) or (self.peek().isdigit()) or (self.peek() == '_')): # while the character is alphabetical, underscored, or a digit read into lexeme
                lex += self.read()

            # different cases for all the reserved words
            if lex == 'null':
                return Token(TokenType.NULL_VAL, 'null', self.line, start_col)
            elif lex == 'true':
                return Token(TokenType.BOOL_VAL, 'true', self.line, start_col)
            elif lex == 'false':
                return Token(TokenType.BOOL_VAL, 'false', self.line, start_col)
            elif lex == 'int':
                return Token(TokenType.INT_TYPE, 'int', self.line, start_col)
            elif lex == 'bool':
                return Token(TokenType.BOOL_TYPE, 'bool', self.line, start_col)
            elif lex == 'void':
                return Token(TokenType.VOID_TYPE, 'void', self.line, start_col)
            elif lex == 'double':
                return Token(TokenType.DOUBLE_TYPE, 'double', self.line, start_col)
            elif lex == 'string':
                return Token(TokenType.STRING_TYPE, 'string', self.line, start_col)
            elif lex == 'struct':
                return Token(TokenType.STRUCT, 'struct', self.line, start_col)
            elif lex == 'array':
                return Token(TokenType.ARRAY, 'array', self.line, start_col)
            elif lex == 'while':
                return Token(TokenType.WHILE, 'while', self.line, start_col)
            elif lex == 'try':
                return Token(TokenType.TRY, 'try', self.line, start_col)
            elif lex == 'as':
                return Token(TokenType.AS, 'as', self.line, start_col)
            elif lex == 'ZeroDivError':
                return Token(TokenType.ZERODIV, 'ZeroDivError', self.line, start_col)
            elif lex == 'catch':
                return Token(TokenType.CATCH, 'catch', self.line, start_col)
            elif lex == 'for':
                return Token(TokenType.FOR, 'for', self.line, start_col)
            elif lex == 'if':
                return Token(TokenType.IF, 'if', self.line, start_col)
            elif lex == 'elseif':
                return Token(TokenType.ELSEIF, 'elseif', self.line, start_col)
            elif lex == 'else':
                return Token(TokenType.ELSE, 'else', self.line, start_col)
            elif lex == 'new':
                return Token(TokenType.NEW, 'new', self.line, start_col)
            elif lex == 'return':
                return Token(TokenType.RETURN, 'return', self.line, start_col)
            elif lex == 'and':
                return Token(TokenType.AND, 'and', self.line, start_col)
            elif lex == 'or':
                return Token(TokenType.OR, 'or', self.line, start_col)
            elif lex == 'not':
                return Token(TokenType.NOT, 'not', self.line, start_col)
            else: # if the lexeme does not match any of the reserved words, it is a ID
                return Token(TokenType.ID, lex, self.line, start_col)
        
        self.error(f"Unknown character'{ch}'", self.line, self.column) # error checking for invalid characters