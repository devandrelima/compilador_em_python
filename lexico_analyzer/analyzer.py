import ply.lex as lex
from pathlib import Path
from tabulate import tabulate

reserved = {
    'event': 'event',
    'situation': 'situation',
    'process': 'process',
    'category': 'category',
    'mixin': 'mixin',
    'phaseMixin': 'phaseMixin',
    'roleMixin': 'roleMixin',
    'historicalRoleMixin': 'historicalRoleMixin',
    'kind': 'kind',
    'collective': 'collective',
    'quantity': 'quantity',
    'quality': 'quality',
    'mode': 'mode',
    'intrisicMode': 'intrisicMode',
    'extrinsicMode': 'extrinsicMode',
    'subkind': 'subkind',
    'phase': 'phase',
    'role': 'role',
    'historicalRole': 'historicalRole',
    'material': 'material',
    'derivation': 'derivation',
    'comparative': 'comparative',
    'mediation': 'mediation',
    'characterization': 'characterization',
    'externalDependence': 'externalDependence',
    'componentOf': 'componentOf',
    'memberOf': 'memberOf',
    'subCollectionOf': 'subCollectionOf',
    'subQualityOf': 'subQualityOf',
    'instantiation': 'instantiation',
    'termination': 'termination',
    'participational': 'participational',
    'participation': 'participation',
    'historicalDependence': 'historicalDependence',
    'creation': 'creation',
    'manifestation': 'manifestation',
    'bringsAbout': 'bringsAbout',
    'triggers': 'triggers',
    'composition': 'composition',
    'aggregation': 'aggregation',
    'inherence': 'inherence',
    'value': 'value',
    'formal': 'formal',
    'constitution': 'constitution',
    'genset': 'genset',
    'disjoint': 'disjoint',
    'complete': 'complete',
    'general': 'general',
    'specifics': 'specifics',
    'where': 'where',
    'package': 'package',
    'number': 'number',
    'string': 'string',
    'boolean': 'boolean',
    'date': 'date',
    'time': 'time',
    'datetime': 'datetime',
    'ordered': 'ordered',
    'const': 'const',
    'derived': 'derived',
    'subsets': 'subsets',
    'redefines': 'redefines',
}

tokens = [
    'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK', 'DOTDOT', 'AGGREGATION_L',
    'AGGREGATION_R', 'ASTERISK', 'AT', 'COLON', 'CLASS_NAME', 'RELATION_NAME',
    'INSTANCE_NAME', 'NEW_TYPE', 'ID'
] + list(reserved.values())

t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACK = r'\['
t_RBRACK = r'\]'
t_DOTDOT = r'\.\.'
t_AGGREGATION_L = r'<>--'
t_AGGREGATION_R = r'--<>'
t_ASTERISK = r'\*'
t_AT = r'@'
t_COLON = r':'
t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'

def t_NEW_TYPE(t):
    r'[a-zA-Z]+DataType'
    return t

def t_INSTANCE_NAME(t):
    r'[a-zA-Z][a-zA-Z_]*\d+'
    return t

def t_CLASS_NAME(t):
    r'[A-Z][a-zA-Z_]*'
    t.type = reserved.get(t.value, 'CLASS_NAME')
    return t

def t_RELATION_NAME(t):
    r'[a-z][a-zA-Z_]*'
    t.type = reserved.get(t.value, 'RELATION_NAME')
    return t
    
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_number(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_error(t):
    print(f"Erro na leitura do caractere: '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

def main_analyser(caminho_codigo_fonte: Path):
    try:
        with open(caminho_codigo_fonte, 'r', encoding='utf-8') as f:
            code_example = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo de exemplo não encontrado em: {caminho_codigo_fonte}")
        return None

    lexer.input(code_example)
    token_list = []
    count = 1
    while True:
        tok = lexer.token()
        if not tok:
            break
        token_list.append({
            'id': count,
            'value': tok.value,
            'type': tok.type,
            'line': tok.lineno
        })
        count += 1
    
    print("Análise Léxica concluída")
    print("\n--- Tabela de Tokens ---")
    print(tabulate(token_list, headers="keys", tablefmt="grid"))
    return token_list