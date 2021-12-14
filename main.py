from rply import LexerGenerator
from rply.token import BaseBox
from rply import ParserGenerator
import sys

#LEXER
lg = LexerGenerator()
#lg.add('INT', r'int')
#lg.add('DOUBLE', r'double')
lg.add('NUMBER', r'\d+')
lg.add('PLUS', r'\+')
lg.add('MINUS', r'-')
lg.add('MUL', r'\*')
lg.add('DIV', r'/')
lg.add('OPEN_PARENS', r'\(')
lg.add('CLOSE_PARENS', r'\)')
lg.add('OPEN_CHAVE', r'{')
lg.add('CLOSE_CHAVE', r'}')
lg.add('PRINT', r'println')
lg.add('EQUAL', r'=')
lg.add('SEMI', r';')
lg.add('IDENTIFIER', r'[a-zA-Z_]([a-zA-Z_0-9]*|_[a-zA-Z_0-9]*)')
lg.add('IF', r'if')
lg.add("ELSE", r'else')
#lg.add('FOR', r'for')
lg.add('WHILE', r'while')
lg.add('EQUIVALENT', r'\=\=')
lg.add('DIFF', r'\!=')
lg.add('GET', r'\>=')
lg.add('LET', r'\<=')
lg.add('GT', r'\>')
lg.add('LT', r'\<')
lg.add('OR', r'\|\|')
lg.add('AND', r'\&\&')
lg.add('NOT', r'\!')
lg.add('READ', r'readln')


lg.ignore(r'\/\*(.*?)\*\/')
lg.ignore('\s+')

lexer = lg.build()

class Node(BaseBox):
    def __init__(self, value):
        self.value = value
        self.children = []
    def eval(self):
        return self.value
class Number(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value

class NoOp(Node):
    def __init__(self, value):
        self.value = value

class UnOp(Node):
    def __init__(self, op, value):
        self.value = op
        self.children = [value]

    def eval(self):
        if self.value == 'POSITIVE':
            return self.children[0].eval()
        elif self.value == 'NEGATIVE':
            return -(self.children[0].eval())
        elif self.value == 'NOT':
            return not(self.children[0].eval())

class BinOp(Node):
    def __init__(self, left, right):
        self.children = [left, right]

class Add(BinOp):
    def eval(self):
        return self.children[0].eval() + self.children[1].eval()

class Sub(BinOp):
    def eval(self):
        return self.children[0].eval() - self.children[1].eval()

class Mul(BinOp):
    def eval(self):
        return self.children[0].eval() * self.children[1].eval()

class Div(BinOp):
    def eval(self):
        return int(self.children[0].eval() / self.children[1].eval())

class And(BinOp):
    def eval(self):
        return self.children[0].eval() and self.children[1].eval()

class Or(BinOp):
    def eval(self):
        return self.children[0].eval() or self.children[1].eval()

class Equivalent(BinOp):
    def eval(self):
        return self.children[0].eval() == self.children[1].eval()

class Diff(BinOp):
    def eval(self):
        return self.children[0].eval() != self.children[1].eval()

class GET(BinOp):
    def eval(self):
        return self.children[0].eval() >= self.children[1].eval()

class LET(BinOp):
    def eval(self):
        return self.children[0].eval() <= self.children[1].eval()

class GT(BinOp):
    def eval(self):
        return self.children[0].eval() > self.children[1].eval()

class LT(BinOp):
    def eval(self):
        return self.children[0].eval() < self.children[1].eval()

class Readln(Node):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return int(input())

class Print(Node):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value.eval()

class While():
    def __init__(self, value):
        self.value = value
    
    def eval(self):
        while self.value[0].eval():
            self.value[1].eval()

class IfElse():
    def __init__(self, value):
        self.value = value
    
    def eval(self):
        if self.value[0].eval():
            self.value[1].eval()
        else:
            if self.value[2] != None:
                self.value[2].eval()

class SymbolTable:
    def __init__(self):
        self.variables = {}

    def peak(self, value):
        return self.variables[value]

    def store(self, value, number):
        self.variables[value] = number
tabela = SymbolTable()

class Peak(Node):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return tabela.peak(self.value)

class Store(Node):
    def __init__(self,left,right):
        self.children = [left, right]
    def eval(self):
        return tabela.store(self.children[0], self.children[1].eval())

class IntVal(Node):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return int(self.value)


class Program():
    def __init__(self, value):
        self.value = value

    def eval(self):
        for i in self.value:
            if not isinstance(i, type(None)):
                if(i.eval() != None):
                    print(i.eval())

#'INT', 'DOUBLE', 'FOR',
pg = ParserGenerator(
    # A list of all token names, accepted by the parser.
    ['NUMBER', 'OPEN_PARENS', 'CLOSE_PARENS', 'OPEN_CHAVE', 'CLOSE_CHAVE','PLUS', 'MINUS', 'MUL', 'DIV', 'PRINT', 'EQUAL', 'SEMI', 'IDENTIFIER',
    'IF', 'ELSE', 'WHILE', 'EQUIVALENT', 'DIFF', 'GET', 'LET', 'GT', 'LT', 'OR', 'AND', 'NOT', 'READ'
    ],
    # A list of precedence rules with ascending precedence, to
    # disambiguate ambiguous production rules.
    precedence=[
        ('left', ['PLUS', 'MINUS']),
        ('left', ['MUL', 'DIV']),
        ('left', ['NOT']),
        ('left', ['OR', 'AND', 'EQUIVALENT', 'DIFF', 'GET', 'LET'] ),
        ('left', ['GT', 'LT'])
    ]
)

@pg.production('input : OPEN_CHAVE program CLOSE_CHAVE ')
def input(p):
    return p[1]

@pg.production('program : statement')
@pg.production('program : program statement')
def prog_state(p):
    if len(p) == 1 :
        return(Program([p[0]]))
    p[0].value += [p[1]]
    return p[0]

@pg.production('statement : println')
@pg.production('statement : read')
def statement(p):
    return p[0]

@pg.production('statement : assignment SEMI')
@pg.production('statement : SEMI')
def statement(p):
    if len(p) > 1:
        return p[0]
    else:
        return None

@pg.production('expression : while')
@pg.production('expression : if')
def expression_bool(p):
    return p[0]

@pg.production('println : PRINT OPEN_PARENS expression CLOSE_PARENS SEMI')
@pg.production('println : PRINT OPEN_PARENS variable CLOSE_PARENS SEMI')
def println(p):
    return Print(p[2])

@pg.production('if : IF OPEN_PARENS bollean-expr CLOSE_PARENS OPEN_CHAVE input CLOSE_CHAVE ELSE OPEN_CHAVE input CLOSE_CHAVE')
@pg.production('if : IF OPEN_PARENS bollean-expr CLOSE_PARENS OPEN_CHAVE input CLOSE_CHAVE')
def IfFunc(p):
    booleanxp = p[2]
    if booleanxp:
        return p[5]
    else:
        if len(p) > 7:
            return p[9]


@pg.production('while : WHILE OPEN_PARENS expression CLOSE_PARENS OPEN_CHAVE input CLOSE_CHAVE')
def WhileFunc(p):
    condElm = p[2]
    loop = p[4]
    return While([condElm, loop])

@pg.production('read : READ OPEN_PARENS CLOSE_PARENS SEMI')
def ReadLn(p):
    return Readln()

@pg.production('expression : PLUS expression')
@pg.production('expression : MINUS expression')
@pg.production('expression : NOT expression')
def expression_unary(p):
    unario = p[0].gettokentype()
    if (unario == 'PLUS'):
        return UnOp('POSITIVE', p[1])
    elif  (unario == 'MINUS'):
        return UnOp('NEGATIVE', p[1])
    elif (unario == 'NOT'):
        return UnOp('NOT', p[1])

@pg.production('expression : NUMBER')
def expression_number(p):
    # p is a list of the pieces matched by the right hand side of the
    # rule
    return IntVal(p[0].getstr())

@pg.production('expression : OPEN_PARENS expression CLOSE_PARENS')
def expression_parens(p):
    return p[1]


@pg.production('assignment : IDENTIFIER EQUAL expression ')
def assignment(p):
    return Store(p[0].getstr(), p[2])

@pg.production('variable : IDENTIFIER')
def variable(p):
    return Peak(p[0].getstr())

@pg.production('expression : variable PLUS expression')
@pg.production('expression : variable MINUS expression')
@pg.production('expression : variable MUL expression')
@pg.production('expression : variable DIV expression')
@pg.production('expression : variable PLUS variable')
@pg.production('expression : variable MINUS variable')
@pg.production('expression : variable MUL variable')
@pg.production('expression : variable DIV variable')
@pg.production('expression : expression PLUS expression')
@pg.production('expression : expression MINUS expression')
@pg.production('expression : expression MUL expression')
@pg.production('expression : expression DIV expression')
###
@pg.production('bollean-expr : bollean-expr AND bollean-expr')
@pg.production('bollean-expr : bollean-expr OR bollean-expr')
@pg.production('bollean-expr : bollean-expr EQUIVALENT expression')
@pg.production('bollean-expr : bollean-expr DIFF bollean-expr')
@pg.production('bollean-expr : bollean-expr GET bollean-expr')
@pg.production('bollean-expr : bollean-expr LET bollean-expr')
@pg.production('bollean-expr : bollean-expr GT bollean-expr')
@pg.production('bollean-expr : bollean-expr LT bollean-expr')

@pg.production('bollean-expr : expression AND expression')
@pg.production('bollean-expr : expression OR expression')
@pg.production('bollean-expr : expression EQUIVALENT expression')
@pg.production('bollean-expr : expression DIFF expression')
@pg.production('bollean-expr : expression GET expression')
@pg.production('bollean-expr : expression LET expression')
@pg.production('bollean-expr : expression GT expression')
@pg.production('bollean-expr : expression LT expression')

def expression_binop(p):
    left = p[0]
    right = p[2]
    if p[1].gettokentype() == 'PLUS':
        return Add(left, right)
    elif p[1].gettokentype() == 'MINUS':
        return Sub(left, right)
    elif p[1].gettokentype() == 'MUL':
        return Mul(left, right)
    elif p[1].gettokentype() == 'DIV':
        return Div(left, right)
    elif p[1].gettokentype() == 'AND':
        return And(left, right)
    elif p[1].gettokentype() == 'OR':
        return Or(left, right)
    elif p[1].gettokentype() == 'EQUIVALENT':
        return Equivalent(left, right)
    elif p[1].gettokentype() == 'DIFF':
        return Diff(left, right)
    elif p[1].gettokentype() == 'GET':
        return GET(left, right)
    elif p[1].gettokentype() == 'LET':
        return LET(left, right)
    elif p[1].gettokentype() == 'GT':
        return GT(left, right)
    elif p[1].gettokentype() == 'LT':
        return LT(left, right)
    else:
        raise AssertionError('Oops, this should not be possible!')

@pg.error
def error_handle(token):
    raise ValueError(token)

parser = pg.build()

def main(entry):
    parser.parse(lexer.lex(entry)).eval()

if __name__ == "__main__":
    main(sys.argv[1])
