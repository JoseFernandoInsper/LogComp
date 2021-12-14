from rply import LexerGenerator
from rply.token import BaseBox
from rply import ParserGenerator
import sys

#LEXER
lg = LexerGenerator()
lg.add('NUMBER', r'\d+')
lg.add('PLUS', r'\+')
lg.add('MINUS', r'-')
lg.add('MUL', r'\*')
lg.add('DIV', r'/')
lg.add('OPEN_PARENS', r'\(')
lg.add('CLOSE_PARENS', r'\)')
lg.add('PRINT', r'println')
lg.add('EQUAL', r'=')
lg.add('SEMI', r'\;')
lg.add('IDENTIFIER', r'[a-zA-Z_]([a-zA-Z_0-9]*|_[a-zA-Z_0-9]*)')
#lg.add('IF', 'if')
#lg.add('WHILE', r'while')


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

class Print(Node):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return self.value.eval()

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

pg = ParserGenerator(
    # A list of all token names, accepted by the parser.
    ['NUMBER','OPEN_PARENS', 'CLOSE_PARENS', 'PLUS', 'MINUS', 'MUL', 'DIV', 'PRINT', 'EQUAL', 'SEMI', 'IDENTIFIER'
    ],
    # A list of precedence rules with ascending precedence, to
    # disambiguate ambiguous production rules.
    precedence=[
        ('left', ['PLUS', 'MINUS']),
        ('left', ['MUL', 'DIV'])
    ]
)

@pg.production('program : statement')
@pg.production('program : program statement')
def prog_state(p):
    if len(p) == 1 :
        return(Program([p[0]]))
    p[0].value += [p[1]]
    return p[0]

@pg.production('statement : println')
def statement(p):
    return p[0]

@pg.production('statement : assignment SEMI')
@pg.production('statement : SEMI')
def statement(p):
    if len(p) > 1:
        return p[0]
    else:
        return None


@pg.production('println : PRINT OPEN_PARENS expression CLOSE_PARENS SEMI')
@pg.production('println : PRINT OPEN_PARENS variable CLOSE_PARENS SEMI')
def println(p):
    return Print(p[2])

@pg.production('expression : PLUS expression')
@pg.production('expression : MINUS expression')
def expression_unary(p):
    unario = p[0].gettokentype()
    if (unario == 'PLUS'):
        return UnOp('POSITIVE', p[1])
    elif  (unario == 'MINUS'):
        return UnOp('NEGATIVE', p[1])


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
