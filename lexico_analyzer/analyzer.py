import ply.lex as lex
from pathlib import Path
from tabulate import tabulate

# role, phase e relator são esteriótipos de classe
# specializes...são esteriótipos de relação
# as outras palavras precisam ser chamadas de palavras reservadas
# nome de classe e de pacote não se diferem, então tem que criar algo que diferencie, ideia: 
# colocar sempre o nome 'Package' quando criar o pacore

reserved = {
    # Estereótipos de classe
    'event': 'CLASS_STEREOTYPE',
    'situation': 'CLASS_STEREOTYPE',
    'process': 'CLASS_STEREOTYPE',
    'category': 'CLASS_STEREOTYPE',
    'mixin': 'CLASS_STEREOTYPE',
    'phaseMixin': 'CLASS_STEREOTYPE',
    'roleMixin': 'CLASS_STEREOTYPE',
    'historicalRoleMixin': 'CLASS_STEREOTYPE',
    'kind': 'CLASS_STEREOTYPE',
    'collective': 'CLASS_STEREOTYPE',
    'quantity': 'CLASS_STEREOTYPE',
    'quality': 'CLASS_STEREOTYPE',
    'mode': 'CLASS_STEREOTYPE',
    'intrisicMode': 'CLASS_STEREOTYPE',
    'extrinsicMode': 'CLASS_STEREOTYPE',
    'subkind': 'CLASS_STEREOTYPE',
    'phase': 'CLASS_STEREOTYPE',
    'role': 'CLASS_STEREOTYPE',
    'historicalRole': 'CLASS_STEREOTYPE',

    # Estereótipos de relações
    'material': 'RELATION_STEREOTYPE',
    'derivation': 'RELATION_STEREOTYPE',
    'comparative': 'RELATION_STEREOTYPE',
    'mediation': 'RELATION_STEREOTYPE',
    'characterization': 'RELATION_STEREOTYPE',
    'externalDependence': 'RELATION_STEREOTYPE',
    'componentOf': 'RELATION_STEREOTYPE',
    'memberOf': 'RELATION_STEREOTYPE',
    'subCollectionOf': 'RELATION_STEREOTYPE',
    'subQualityOf': 'RELATION_STEREOTYPE',
    'instantiation': 'RELATION_STEREOTYPE',
    'termination': 'RELATION_STEREOTYPE',
    'participational': 'RELATION_STEREOTYPE',
    'participation': 'RELATION_STEREOTYPE',
    'historicalDependence': 'RELATION_STEREOTYPE',
    'creation': 'RELATION_STEREOTYPE',
    'manifestation': 'RELATION_STEREOTYPE',
    'bringsAbout': 'RELATION_STEREOTYPE',
    'triggers': 'RELATION_STEREOTYPE',
    'composition': 'RELATION_STEREOTYPE',
    'aggregation': 'RELATION_STEREOTYPE',
    'inherence': 'RELATION_STEREOTYPE',
    'value': 'RELATION_STEREOTYPE',
    'formal': 'RELATION_STEREOTYPE',
    'constitution': 'RELATION_STEREOTYPE',

    # Palavras reservadas
    'genset': 'RESERVED_WORD',
    'disjoint': 'RESERVED_WORD',
    'complete': 'RESERVED_WORD',
    'general': 'RESERVED_WORD',
    'specifics': 'RESERVED_WORD',
    'where': 'RESERVED_WORD',
    'package': 'RESERVED_WORD',

    # Tipos de dados nativos
    'number': 'NATIVE_TYPE',
    'string': 'NATIVE_TYPE',
    'boolean': 'NATIVE_TYPE',
    'date': 'NATIVE_TYPE',
    'time': 'NATIVE_TYPE',
    'datetime': 'NATIVE_TYPE',

    # Meta-atributos
    'ordered': 'META_ATTRIBUTE',
    'const': 'META_ATTRIBUTE',
    'derived': 'META_ATTRIBUTE',
    'subsets': 'META_ATTRIBUTE',
    'redefines': 'META_ATTRIBUTE',
}

tokens = [
    'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK', 'DOTDOT', 'AGGREGATION_L',
    'AGGREGATION_R', 'ASTERISK', 'AT', 'COLON', 'CLASS_NAME', 'RELATION_NAME',
    'INSTANCE_NAME', 'NEW_TYPE', 'ID'
] + list(set(reserved.values()))

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

def t_error(t):
    # print(f"Não leu caractere: '{t.value[0]}' na linha {t.lexer.lineno}")
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
    while True:
        tok = lexer.token()
        if not tok:
            break
        token_list.append({
            'value': tok.value,
            'type': tok.type,
            'line': tok.lineno
        })
    
    print("Análise Léxica concluída")
    print("\n--- Tabela de Tokens ---")
    print(tabulate(token_list, headers="keys", tablefmt="grid"))
    return token_list