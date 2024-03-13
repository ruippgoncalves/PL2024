from datetime import date
import json
import ply.lex as lex
import sys

tokens = [
    'MOEDA',
    'LISTAR',
    'SELECIONAR',
    'SAIR',
    'SALDO',
    'NOVO',
    'STOCK'
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
    r'(?i:selecionar\s+(\w+))'
    t.value = t.value.split()[-1]
    return t

def t_NOVO(t):
    r'(?i:novo\s+(\w+)\s+(\d+)\s+(\d+(.\d{1,2})?)\s+.*)'

    t.value = t.value.split()
    t.value[2] = int(t.value[2])
    t.value[3] = float(t.value[3])
    t.value = (t.value[1], t.value[2], t.value[3], ' '.join(t.value[4:]))
    
    return t

def t_STOCK(t):
    r'(?i:stock\s+(\w+)\s+\d+)'

    t.value = t.value.split()
    t.value = (t.value[1], int(t.value[2]))

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

def read_products():
    with open('data.json', 'r') as file:
        data = json.load(file)

    return {product['cod']: product for product in data}

def write_products():
    with open('data.json', 'w') as file:
        json.dump([{"cod": k, **v} for k, v in products.items()], file)
        

products = read_products()

cur = 0

def novo(cod, nome, qtd, preco):
    global products

    products[cod] = { "nome": nome, "quant": qtd, "preco": preco }

def stock(cod, qtd):
    products[cod]["quant"] += qtd

def listar():
    global products

    print('maq:')
    print("cod | nome | quantidade | preço")
    print("-------------------------------")

    for k, v in products.items():
        print(f"{k} | {v['nome']} | {v['quant']} | {v['preco']}")

    print()

def coin(e, c):
    global cur

    cur += e * 100 + c

def saldo():
    global cur
    
    print(f"maq: Saldo = {cur // 100}e{'%02d' % (cur % 100)}c")

def sair():
    global cur

    r = ['2e', '1e', '50c', '20c', '10c', '5c', '2c', '1c']
    m = [200, 100, 50, 20, 10, 5, 2, 1]
    qtd = [0, 0, 0, 0, 0, 0, 0, 0]
    i = 0
    
    while cur != 0:
        if cur >= m[i]:
            qtd[i] += 1
            cur -= m[i]
        else:
            i += 1

    if not all(x == 0 for x in qtd):
        print('maq: Pode retirar o troco: ', end='')

        for i, t in enumerate(qtd):
            if t != 0:
                print(f'{t}x {r[i]}, ', end='')

        print('\b\b.')
    
    print("maq: Até à próxima")


def select(p):
    global cur
    global products

    if p not in products:
        print('maq: Produto inexistente')
        return

    pr = int(products[p]['preco'] * 100)

    if products[p]['quant'] <= 0:
        print('maq: não tem quantidade suficiente')
    elif cur > pr:
        print(f'maq: Pode retirar o produto dispensado "{products[p]["nome"]}"')

        products[p]['quant'] -= 1
        cur -= pr

        saldo()
    else:
        print("maq: Saldo insufuciente para satisfazer o seu pedido")
        print(f"maq: Saldo = {cur // 100}e{cur % 100}c; Pedido {pr // 100}e{'%02d' % (pr % 100)}c")


print(f'maq: {date.today()}, Stock carregado, Estado atualizado.')
print('maq: Bom dia. Estou disponível para atender o seu pedido.')

print('>> ', end='', flush=True)

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
        elif tok.type == 'SALDO':
            saldo()
        elif tok.type == 'SAIR':
            sair()
        elif tok.type == 'NOVO':
            novo(tok.value[0], tok.value[3], tok.value[1], tok.value[2])
        elif tok.type == 'STOCK':
            stock(tok.value[0], tok.value[1])
        else:
            print("Comando inválido")

    print('>> ', end='', flush=True)

