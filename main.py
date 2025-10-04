from pathlib import Path
from lexico_analyzer.analyzer import main_analyser

def listar_e_mapear_exemplos(caminho_da_pasta: str):

    pasta = Path(caminho_da_pasta)
    mapa_de_arquivos = {}

    if not pasta.is_dir():
        print(f"ERRO: A pasta '{caminho_da_pasta}' não foi encontrada.")
        return None

    arquivos_tonto = sorted([item for item in pasta.iterdir() if item.is_file() and item.suffix == '.tonto'])
    
    if not arquivos_tonto:
        print(f"Nenhum arquivo .tonto encontrado na pasta '{caminho_da_pasta}'.")
        return None

    print("--- Arquivos de Exemplo Tonto Disponíveis ---")
    
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
        
        main_analyser(caminho_do_arquivo_escolhido)
    else:
        print(f"ERRO: Opção '{escolha}' inválida.")