import ply.lex as lex
import re

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
    'RELATION_ID', 'INSTANCE_ID', 'CARDINALITY', 'ERROR', 'NEWLINE', 'NUMBER', 'functional_complexes'
] + list(set(reserved.values()))

literals = ['(', ')', '{', '}', '.', ',', '+', '<', '>', '@', '-',
            '*', ':']

t_DOTDOT = r'\.\.'
t_ignore = ' \t'
t_ignore_COMMENT = r'\#.*'

def t_FUNCTIONAL_COMPLEXES(t):
    r'functional-complexes'
    t.type = 'functional_complexes'
    return t

def t_CARDINALITY(t):
    r'\[[\d\*\.]+\]'
    return t

def t_NEW_TYPE(t):
    r'[a-zA-Z]+DataType'
    return t

def t_INSTANCE_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*[0-9]'
    t.type = reserved.get(t.value, 'INSTANCE_ID')
    return t

def t_CLASS_ID(t):
    r'[A-Z_][a-zA-Z_]*'
    t.type = reserved.get(t.value, 'CLASS_ID')
    return t

def t_RELATION_ID(t):
    r'[a-z_][a-zA-Z_]*'
    t.type = reserved.get(t.value, 'RELATION_ID')
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value) 
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
    tok.value = illegal_char
    tok.lineno = t.lexer.lineno
    tok.lexpos = t.lexer.lexpos

    t.lexer.skip(1)
    return tok

lexer = lex.lex(reflags=re.UNICODE)