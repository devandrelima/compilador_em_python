from pathlib import Path
import os
import sys
from lexico_analyzer.lexical_counter import lexical_counter_analyser
from syntactic_analyzer.analyser import analisar_sintaxe
from semantic_analyzer.analyzer import AnalisadorSemantico

# Dicionário global para armazenar as ASTs de todos os arquivos processados
ASTs_GLOBAIS = {}

def resolver_caminho_arquivo(nome_import, pasta_base):
    """
    Tenta encontrar o arquivo .tonto correspondente ao import
    """
    caminho = pasta_base / f"{nome_import}.tonto"
    
    if not caminho.exists():
        # Tenta procurar ignorando maiúsculas/minúsculas se não achar de primeira
        for arquivo in pasta_base.iterdir():
            if arquivo.stem.lower() == nome_import.lower() and arquivo.suffix == '.tonto':
                return arquivo
        return None
    
    return caminho

def processar_arquivo_recursivo(caminho_arquivo: Path, pasta_base: Path, visitados: set):
    """
    Lê, analisa (léxico e sintático) e processa imports recursivamente
    """
    nome_modulo = caminho_arquivo.stem

    # Evita ciclos (A importa B, B importa A) e reprocessamento
    if nome_modulo in visitados:
        return
    
    print(f"\n\n\n\n{'{'*20}  Processando: {nome_modulo}  {'}'*20}\n")
    visitados.add(nome_modulo)

    # Leitura do Código
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            codigo_fonte = f.read()
    except FileNotFoundError:
        print(f"[ERRO] Arquivo não encontrado: {caminho_arquivo}")
        return

    print(f"-> Executando Análise Léxica de {nome_modulo}...")
    
    lexical_counter_analyser(caminho_arquivo, codigo_fonte)

    # Análise Sintática (Gera AST)
    print(f"-> Executando Análise Sintática de {nome_modulo}...")
    ast = analisar_sintaxe(codigo_fonte, nome_modulo)

    if not ast:
        print(f"[ERRO CRÍTICO] Falha na análise sintática de {nome_modulo}. Dependências podem quebrar.")
        return

    # Salva a AST no dicionário global para o Analisador Semântico
    ASTs_GLOBAIS[nome_modulo] = ast

    # Processar Imports da AST para Recursão
    lista_imports = ast[1]

    if lista_imports:
        nomes_imports = [imp[1] for imp in lista_imports]
        print(f"\n> Imports detectados: {nomes_imports}")
        
        for imp in lista_imports:
            # Estrutura do import na AST: ('import', 'NomeDaClasse')
            nome_importado = imp[1]
            
            caminho_import = resolver_caminho_arquivo(nome_importado, pasta_base)
            
            if caminho_import:
                # Chamada Recursiva
                processar_arquivo_recursivo(caminho_import, pasta_base, visitados)
            else:
                print(f"\n[AVISO] Arquivo referente ao import '{nome_importado}' não encontrado na pasta.")

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
    
    pasta_de_exemplos = Path('./tonto_examples')
    
    mapa = listar_e_mapear_exemplos(str(pasta_de_exemplos))

    if mapa:
        escolha = input('\nEscolha o número do arquivo PRINCIPAL para compilar: ')
        caminho_principal = mapa.get(escolha)
        
        if caminho_principal:
            print(f'\n>>> Iniciando compilação a partir de: {caminho_principal.name}')
            
            ASTs_GLOBAIS.clear()
            conjunto_visitados = set()
            
            # Isso vai ler o arquivo escolhido E todos os arquivos que ele importar
            processar_arquivo_recursivo(caminho_principal, pasta_de_exemplos, conjunto_visitados)
            
            print(f"\n\nASTs carregadas na memória global: {list(ASTs_GLOBAIS.keys())}")
            
            if ASTs_GLOBAIS:
                semantico = AnalisadorSemantico(ASTs_GLOBAIS)
                semantico.analisar(caminho_principal.name)
            else:
                print("Nenhuma AST foi gerada. A análise semântica foi cancelada")
            
        else:
            print(f"ERRO: Opção '{escolha}' inválida.")