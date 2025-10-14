import ply.lex as lex
from pathlib import Path
from tabulate import tabulate

reserved = {
    'import':'import',
    'relator': 'relator',
    'specializes': 'specializes',
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
    'COMPOSITION_L', 'COMPOSITION_R', 'COMPOSITION_LO', 'COMPOSITION_RO', 
    'ASSOCIATION', 'DOTDOT', 'CLASS_NAME', 'NEW_TYPE', 'ID', 'CLASS_ID', 
    'RELATION_ID', 'CARDINALITY'
] + list(reserved.values())

literals = ['(', ')', '{', '}', '.', ',', '+', '-', '<', '>', '@',
            '*', ':']

t_DOTDOT = r'\.\.'
t_COMPOSITION_L = r'<>--'
t_COMPOSITION_R = r'--<>'
t_COMPOSITION_LO = r'<o>--'
t_COMPOSITION_RO = r'--<o>'
t_ASSOCIATION = r'--'
t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'

def t_CARDINALITY(t):
    r'\[[\d\*\.]+\]'
    return t

def t_NEW_TYPE(t):
    r'[a-zA-Z]+DataType'
    return t


def t_CLASS_ID(t):
    r'[A-Z_][a-zA-Z_]*'
    t.type = reserved.get(t.value, 'CLASS_ID')
    if (t.type == 'CLASS_ID'):
        t.lexer.class_set.add(t.value)
    return t


def t_RELATION_ID(t):
    r'[a-z_][a-zA-Z_]*'
    t.type = reserved.get(t.value, 'RELATION_ID')
    if (t.type == 'RELATION_ID'):
        t.lexer.relation_count += 1
    return t


def t_INSTANCE_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*[0-9]*'
    t.type = reserved.get(t.value, 'INSTANCE_ID')
    if (t.type == 'INSTANCE_ID'):
        t.lexer.instance_count += 1
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
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
    print(f"Erro na leitura do caractere: '{
          t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)


lexer = lex.lex()
lexer.relation_count = 0
lexer.instance_count = 0
lexer.class_set = set()


def main_analyser(caminho_codigo_fonte: Path):
    try:
        with open(caminho_codigo_fonte, 'r', encoding='utf-8') as f:
            code_example = f.read()
    except FileNotFoundError:
        print(f"ERRO: Arquivo de exemplo não encontrado em: {
              caminho_codigo_fonte}")
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
            'line': tok.lineno,
        })
        count += 1

    print("Análise Léxica concluída")
    print("\n--- Tabela de Tokens ---")
    print(tabulate(token_list, headers="keys", tablefmt="grid"))
    print("QUANTIDADE DE CLASSES: " + str(len(lexer.class_set)))
    print("QUANTIDADE DE RELACOES: " + str(lexer.relation_count))
    print("QUANTIDADE DE INSTANCIAS: " + str(lexer.instance_count))
    return token_list
