import re

import ply.lex as lex
import sys

tokens = [
    'MOEDA',
    'LISTAR',
    'SELECIONAR',
    'SAIR',
    'SALDO',
]

t_LISTAR = r'(?i:listar)'
t_SAIR = r'(?i:sair)'
t_SALDO = r'(?i:saldo)'

def parse_coin(c):
    if c[-1] == 'e':
        return int(c[:-1]), 0
    else:
        return 0, int(c[:-1])

def t_MOEDA(t):
    r'(?i:moeda)(\s*(1c|2c|5c|10c|20c|50c|1e|2e),)*(\s*(1c|2c|5c|10c|20c|50c|1e|2e)\.)'
    # Seriously, it does not accepts formated here

    t.value = t.value[6:-1]
    t.value = t.value.split(',')
    t.value = [x.strip() for x in t.value]
    t.value = [parse_coin(x) for x in t.value]

    return t

def t_SELECIONAR(t):
    r'(?i:selecionar\s+(\d+))'
    t.value = int(t.value[10:])
    return t


t_ignore = ' \t\r'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)


lexer = lex.lex()

#tests = """
#LiStAr
#moeda 1c,2c,5c,10c,20c,50c,1e,2e.
#selecionar 5
#saldo
#sair
#"""
#lexer.input(tests)

#for tok in lexer:
#   print(tok)

products = [
    {
        'name': 'Agua',
        'price': (0, 65)
    },
    {
        'name': 'Cafe',
        'price': (0, 80)
    },
    {
        'name': 'Coca-Cola',
        'price': (1, 0)
    },
    {
        'name': 'Sumo',
        'price': (1, 20)
    },
    {
        'name': 'Sandes',
        'price': (1, 50)
    },
    {
        'name': 'Chocolate',
        'price': (1, 25)
    },
]

cur = (0, 0)

def listar():
    for i, product in enumerate(products):
        print(f"{i} - {product['name']} - {product['price'][0]}e{product['price'][1]}c")

def coin(e, c):
    global cur

    cur = (cur[0] + e, cur[1] + c)

    if cur[1] >= 100:
        cur = (cur[0] + 1, cur[1] - 100)

def saldo(is_troco=False):
    if is_troco:
        print(f"Troco = {cur[0]}e{cur[1]}c")
    else:
        print(f"Saldo = {cur[0]}e{cur[1]}c")

def select(p):
    global cur

    if cur[0] > products[p]['price'][0] or (cur[0] == products[p]['price'][0] and cur[1] >= products[p]['price'][1]):
        print(f"Vending {products[p]['name']}")

        cur = (cur[0] - products[p]['price'][0], cur[1] - products[p]['price'][1])

        if cur[1] < 0:
            cur = (cur[0] - 1, cur[1] + 100)
    else:
        print("Saldo insuficiente")

for line in sys.stdin:
    lexer.input(line)

    for tok in lexer:
        if tok.type == 'MOEDA':
            for e, c in tok.value:
                coin(e, c)
            saldo()
        elif tok.type == 'LISTAR':
            listar()
        elif tok.type == 'SELECIONAR':
            select(tok.value)
            saldo()
        elif tok.type == 'SALDO':
            saldo()
        elif tok.type == 'SAIR':
            saldo(is_troco=True)
        else:
            print("Comando inválido")
