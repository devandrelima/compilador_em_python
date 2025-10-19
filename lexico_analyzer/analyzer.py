import ply.lex as lex
from pathlib import Path
from tabulate import tabulate
import re

tipos = {
    'event': 'estereotipo_classe',
    'situation': 'estereotipo_classe',
    'process': 'estereotipo_classe',
    'category': 'estereotipo_classe',
    'mixin': 'estereotipo_classe',
    'phaseMixin': 'estereotipo_classe',
    'roleMixin': 'estereotipo_classe',
    'historicalRoleMixin': 'estereotipo_classe',
    'kind': 'estereotipo_classe',
    'collective': 'estereotipo_classe',
    'quantity': 'estereotipo_classe',
    'quality': 'estereotipo_classe',
    'mode': 'estereotipo_classe',
    'intrisicMode': 'estereotipo_classe',
    'extrinsicMode': 'estereotipo_classe',
    'subkind': 'estereotipo_classe',
    'phase': 'estereotipo_classe',
    'role': 'estereotipo_classe',
    'historicalRole': 'estereotipo_classe',

    'material': 'estereotipo_relacao',
    'derivation': 'estereotipo_relacao',
    'comparative': 'estereotipo_relacao',
    'mediation': 'estereotipo_relacao',
    'characterization': 'estereotipo_relacao',
    'externalDependence': 'estereotipo_relacao',
    'componentOf': 'estereotipo_relacao',
    'memberOf': 'estereotipo_relacao',
    'subCollectionOf': 'estereotipo_relacao',
    'subQualityOf': 'estereotipo_relacao',
    'instantiation': 'estereotipo_relacao',
    'termination': 'estereotipo_relacao',
    'participational': 'estereotipo_relacao',
    'participation': 'estereotipo_relacao',
    'historicalDependence': 'estereotipo_relacao',
    'creation': 'estereotipo_relacao',
    'manifestation': 'estereotipo_relacao',
    'bringsAbout': 'estereotipo_relacao',
    'triggers': 'estereotipo_relacao',
    'composition': 'estereotipo_relacao',
    'aggregation': 'estereotipo_relacao',
    'inherence': 'estereotipo_relacao',
    'value': 'estereotipo_relacao',
    'formal': 'estereotipo_relacao',
    'constitution': 'estereotipo_relacao',

    'genset': 'palavra_reservada',
    'disjoint': 'palavra_reservada',
    'complete': 'palavra_reservada',
    'general': 'palavra_reservada',
    'specifics': 'palavra_reservada',
    'where': 'palavra_reservada',
    'package': 'palavra_reservada',
    'import': 'palavra_reservada',
    'functional-complexes': 'palavra_reservada',
    'specializes': 'palavra_reservada',

    'number': 'dado_nativo',
    'string': 'dado_nativo',
    'boolean': 'dado_nativo',
    'date': 'dado_nativo',
    'time': 'dado_nativo',
    'datetime': 'dado_nativo',

    'ordered': 'meta_atributo',
    'const': 'meta_atributo',
    'derived': 'meta_atributo',
    'subsets': 'meta_atributo',
    'redefines': 'meta_atributo'
}

reserved = {
    'import': 'import',
    'relator': 'relator',
    'specializes': 'specializes',
    'functional-complexes': 'functional_complexes',
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
    'RELATION_ID','INSTANCE_ID' ,'CARDINALITY', 'ERROR', 'NEWLINE', 'NUMBER','functional_complexes' 
] + list(reserved.values())

literals = ['(', ')', '{', '}', '.', ',', '+', '<', '>', '@', '-',
            '*', ':']

t_DOTDOT = r'\.\.'
t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'

def t_FUNCTIONAL_COMPLEXES(t):
    r'functional-complexes'
    t.type = 'functional_complexes'
    t.value = {'value': t.value, 'type': tipos.get(t.value, 'palavra_reservada')}
    return t

def t_CARDINALITY(t):
    r'\[[\d\*\.]+\]'
    return t


def t_NEW_TYPE(t):
    r'[a-zA-Z]+DataType'
    t.value = {'value': t.value, 'type': tipos.get(t.value, 'new_type')}
    return t


def t_CLASS_ID(t):
    r'[A-Z_][a-zA-Z_]*'
    t.type = reserved.get(t.value, 'CLASS_ID')
    t.value = {'value': t.value, 'type': tipos.get(t.value, 'classe')}
    if (t.type == 'CLASS_ID'):
        t.lexer.class_set.add(t.value['value'])
    return t


def t_INSTANCE_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*[0-9]'
    t.type = reserved.get(t.value, 'INSTANCE_ID')
    t.value = {'value': t.value, 'type': tipos.get(t.value, 'instancia')}
    if (t.type == 'INSTANCE_ID'):
        t.lexer.instance_set.add(t.value['value'])
    return t


def t_RELATION_ID(t):
    r'[a-z_][a-zA-Z_]*'
    t.type = reserved.get(t.value, 'RELATION_ID')
    t.value = {'value': t.value, 'type': tipos.get(t.value, 'relacao')}
    if (t.type == 'RELATION_ID'):
        t.lexer.relation_set.add(t.value['value'])
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    t.value = {'value': t.value, 'type': tipos.get(t.value, 'id')}
    return t


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_NUMBER(t):
    r'\d+'
    t.value = {'value': int(t.value), 'type': tipos.get(t.value, 'number')}
    return t


def t_COMPOSITION_L(t):
    r'<>--'
    return t


def t_COMPOSITION_R(t):
    r'--<>'
    return t


def t_COMPOSITION_LO(t):
    r'<o>--'
    return t


def t_COMPOSITION_RO(t):
    r'--<o>'
    return t


def t_ASSOCIATION(t):
    r'--'
    return t

def t_error(t):
    illegal_char = t.value[0]
    print(f"Erro Léxico: Caractere '{illegal_char}' não reconhecido na linha {t.lexer.lineno}")


    tok = lex.LexToken()
    tok.type = 'ERROR'
    tok.value = {'value': illegal_char, 'type': 'error'}
    tok.lineno = t.lexer.lineno
    tok.lexpos = t.lexer.lexpos
    
    t.lexer.skip(1)  
    return tok       

lexer = lex.lex(reflags=re.UNICODE)
lexer.class_set = set()
lexer.relation_set = set()
lexer.instance_set = set()

type_count = {}


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

        val = tok.value
        classification = ''

        if isinstance(tok.value, dict):
            val = tok.value['value']
            classification = tok.value['type']

            if type_count.get(classification) and val not in type_count.get(classification):
                type_count[classification]['contador'] += 1
                type_count[classification]['lista'].append(val)
            else:
                type_count[classification] = {'lista': [val], 'contador': 1}

        last_newline = code_example.rfind('\n', 0, tok.lexpos)
        column = (tok.lexpos - last_newline)

        token_list.append({
            'id': count,
            'value': val,
            'type': tok.type,
            'line': tok.lineno,
            'column': column,
            'classification': classification
        })
        count += 1

    print("Análise Léxica concluída")
    print("\n--- Tabela de Tokens ---")
    print(tabulate(token_list, headers="keys", tablefmt="grid"))

    type_count_list = []

    for key, value in type_count.items():
        type_count_list.append({'classification': key, 'quantity': value['contador']})

    print(tabulate(type_count_list, headers="keys", tablefmt="grid"))

    return token_list