from pathlib import Path
from lexico_analyzer.lexical_counter import main_analyser
from syntactic_analyzer.analyser import analisar_sintaxe

def importar_codigo(caminho_codigo_fonte):
    try:
        with open(caminho_codigo_fonte, 'r', encoding='utf-8') as f:
            code_example = f.read()

        return code_example
    
    except FileNotFoundError:
        print(f"ERRO: Arquivo de exemplo não encontrado em: {
              caminho_codigo_fonte}")
        return None


def listar_e_mapear_exemplos(caminho_da_pasta: str):
    """
    Busca arquivos .tonto na pasta especificada, imprime um menu numerado
    e retorna um dicionário mapeando o índice
    """

    pasta = Path(caminho_da_pasta)
    mapa_de_arquivos = {}

    if not pasta.is_dir():
        print(f"ERRO: A pasta '{caminho_da_pasta}' não foi encontrada.")
        return None

    arquivos_tonto = sorted([item for item in pasta.iterdir() if item.is_file() and item.suffix == '.tonto'])
    
    if not arquivos_tonto:
        print(f"Nenhum arquivo .tonto encontrado na pasta '{caminho_da_pasta}'.")
        return None

    print("\n\n--- Arquivos de Exemplo Tonto Disponíveis ---\n")
    
    for i, arquivo in enumerate(arquivos_tonto):
        chave_id = f'{i:02}'
    
        mapa_de_arquivos[chave_id] = arquivo
        
        print(f"[{chave_id}]  {arquivo.name}")
    
    return mapa_de_arquivos

if __name__ == "__main__":
    
    pasta_de_exemplos = './tonto_examples'
    
    mapa = listar_e_mapear_exemplos(pasta_de_exemplos)

    escolha = input('\nEscolha o número do arquivo de exemplo: ')
    
    caminho_do_arquivo_escolhido = mapa.get(escolha)
    
    if caminho_do_arquivo_escolhido:
        print(f'Path do exemplo selecionado: {caminho_do_arquivo_escolhido}')
        print('\nExecutando a análise léxica...')
        
        codigo_fonte = importar_codigo(caminho_do_arquivo_escolhido)

        main_analyser(caminho_do_arquivo_escolhido, codigo_fonte)
        
        nome_exemplo = caminho_do_arquivo_escolhido.stem
        
        analisar_sintaxe(codigo_fonte, nome_exemplo)

    else:
        print(f"ERRO: Opção '{escolha}' inválida.")