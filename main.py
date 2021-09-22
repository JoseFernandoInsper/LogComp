from rply import LexerGenerator
from rply.token import BaseBox
from rply import ParserGenerator
import sys


lg = LexerGenerator()
lg.add('NUMBER', r'\d+')
lg.add('PLUS', r'\+')
lg.add('MINUS', r'-')
lg.add('MUL', r'\*')
lg.add('DIV', r'/')
lg.add('OPEN_PARENS', r'\(')
lg.add('CLOSE_PARENS', r'\)')

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

class IntVal(Node):
    def __init__(self, value):
        self.value = value

    def eval(self):
        return int(self.value)

class UnOp(Node):
    def __init__(self, op, value):
        self.value = op
        self.children = [value]

    def eval(self):
        if self.value == 'POSITIVE':
            return self.children[0].eval()
        elif self.value == 'NEGATIVE':
            return -(self.children[0].eval())


pg = ParserGenerator(
    # A list of all token names, accepted by the parser.
    ['NUMBER','OPEN_PARENS', 'CLOSE_PARENS', 'PLUS', 'MINUS', 'MUL', 'DIV'
    ],
    # A list of precedence rules with ascending precedence, to
    # disambiguate ambiguous production rules.
    precedence=[
        ('left', ['PLUS', 'MINUS']),
        ('left', ['MUL', 'DIV'])
    ]
)

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

parser = pg.build()

def main(entry):
    print(parser.parse(lexer.lex(entry)).eval())

if __name__ == "__main__":
    main(sys.argv[1])
