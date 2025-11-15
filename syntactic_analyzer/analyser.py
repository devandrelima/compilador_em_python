import ply.yacc as yacc
from lexico_analyzer.lexer_puro import tokens, lexer

def p_programa(p):
    'programa : declaracao_pacote'
    print("Análise Sintática: Sucesso! Programa Tonto reconhecido.")
    p[0] = p[1] 

def p_declaracao_pacote(p):
    'declaracao_pacote : package CLASS_ID'
    p[0] = ('pacote', p[2])
    print(f"Sintático: Encontrada declaração de pacote '{p[2]}'")

def p_error(p):
    if p:
        print(f"Erro de Sintaxe: Token inesperado '{p.value}' (Tipo: {p.type}) na linha {p.lineno}")
    else:
        print("Erro de Sintaxe: Fim de arquivo inesperado! (Faltando '}'?)")

parser = yacc.yacc()

def analisar_sintaxe(texto_codigo: str):
    return parser.parse(texto_codigo, lexer=lexer)