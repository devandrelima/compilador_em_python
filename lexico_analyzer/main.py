# --- Arquivo: main.py ---
from lark import Lark
import json

# Carrega a gramática
with open('grammar.lark', 'r', encoding='utf-8') as i:
    tonto_grammar = i.read()

# Carrega o código exemplo
number_example = '00'

with open(f'../tonto_examples/{number_example}.tonto', 'r', encoding='utf-8') as j:
    code_example = j.read()

# Cria a instância do parser Lark com nossa gramática
parser_tonto = Lark(tonto_grammar, start='start')

tokens = parser_tonto.lex(code_example)

token_list = []

for token in tokens:

    token_dict = {
        'type': token.type,
        'value': token.value,
        'line': token.line
    }

    token_list.append(token_dict)

with open('tokens.json', 'w', encoding='utf-8') as k:
    json.dump(token_list, k, indent=4, ensure_ascii=False)

print(f"Análise Léxica concluída, tokens do exemplo {number_example}.tonto no arquivo tokens.json")