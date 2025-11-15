import ply.yacc as yacc

from lexico_analyzer.analyzer import tokens

# 2. A REGRA INICIAL (Start Symbol)
# Esta é a regra mais importante. Ela define o que é um "programa Tonto" completo.
# Com base no documento, um programa começa com um pacote.
# 'p_program' é apenas um nome de função, o que importa é a docstring.
def p_programa(p):
    'programa : declaracao_pacote'
    # Esta é a regra gramatical: "Um programa é uma declaração de pacote"
    # Por enquanto, não faremos nada, só reconheceremos a estrutura.
    print("Sucesso! Programa Tonto reconhecido.")
    pass

# 3. REGRA PARA DECLARAÇÃO DE PACOTE (Regra 1 do PDF)
# Vamos definir o que é uma 'declaracao_pacote'
# [cite_start]O PDF diz: "package myPackage" [cite: 18]
# No nosso léxico, isso são dois tokens: 'package' e 'CLASS_ID'
def p_declaracao_pacote(p):
    'declaracao_pacote : package CLASS_ID'
    # A gramática é: "Uma declaração de pacote é o token 'package' 
    # seguido de um token 'CLASS_ID'"
    pass

# (Futuramente, adicionaremos mais regras aqui, como 'declaracao_classe', etc.)

# 4. MANIPULAÇÃO DE ERROS SINTÁTICOS
# Esta função é chamada automaticamente pelo YACC quando
# ele encontra um token que não se encaixa na gramática.
def p_error(p):
    if p:
        print(f"Erro de sintaxe próximo ao token '{p.value}' (Tipo: {p.type}) na linha {p.lineno}")
    else:
        print("Erro de sintaxe: Fim inesperado do arquivo!")

# 5. CONSTRUINDO O PARSER (O ANALISADOR SINTÁTICO)
# O YACC lê todas as funções p_... e constrói o analisador.
parser = yacc.yacc()

# 6. FUNÇÃO PRINCIPAL PARA O main.py CHAMAR
def analisar_sintaxe(texto_codigo):
    """
    Função principal que o main.py usará.
    Ela recebe o código, chama o léxico e inicia a análise sintática.
    """
    # Importamos o lexer (a máquina léxica)
    from lexico_analyzer.analyzer import lexer
    
    # parser.parse() inicia a análise.
    # Ele pede tokens ao 'lexer' automaticamente.
    return parser.parse(texto_codigo, lexer=lexer)