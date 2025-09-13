import json
from pathlib import Path
from lark import Lark

def execute_lexico_analyzer(number_example):
    try:
        script_dir = Path(__file__).parent
        grammar_path = script_dir / 'grammar.lark'
        example_path = script_dir.parent / 'tonto_examples' / f'{number_example}.tonto'
        tokens_output_path = script_dir / 'tokens.json'
        
        with open(grammar_path, 'r', encoding='utf-8') as i:
            tonto_grammar = i.read()

        with open(example_path, 'r', encoding='utf-8') as j:
            code_example = j.read()

        parser_tonto = Lark(tonto_grammar, start='start')
        tokens = parser_tonto.lex(code_example)

        token_list = []

        for token in tokens:
            token_list.append({
                'type': token.type,
                'value': token.value,
                'line': token.line
            })

        with open(tokens_output_path, 'w', encoding='utf-8') as k:
            json.dump(token_list, k, indent=4, ensure_ascii=False)

        print(f"Resultado salvo em '{tokens_output_path.name}'")

    except FileNotFoundError as e:
        print(f"Arquivo não encontrado: {e.filename}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")