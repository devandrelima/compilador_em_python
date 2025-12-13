# semantic_analyzer/analyzer.py

class TabelaDeSimbolos:
    """
    Representa a visão geral da ontologia.
    Armazena todas as classes, relações e generalizações encontradas
    em todos os arquivos processados.
    """
    def __init__(self):
        # Dicionário de Classes:
        self.classes = {}
        
        # Lista de Relações (para validações futuras de conectividade)
        self.relacoes = []
        
        # Lista de Generalization Sets (Gensets)
        self.gensets = []
        
        # Lista de erros semânticos encontrados
        self.erros = []
        
        # Lista de padrões identificados
        self.padroes_identificados = []

    def adicionar_classe(self, nome, estereotipo, pais, pacote):
        """Registra uma classe encontrada na AST."""
        if nome in self.classes:
            # Se for do mesmo pacote, é duplicação. Se for de outro, pode ser redefinição ou erro.
            pacote_existente = self.classes[nome]['pacote']
            if pacote_existente == pacote:
                self.erros.append(f"Erro Semântico: Classe '{nome}' redeclarada no mesmo pacote '{pacote}'.")
        else:
            self.classes[nome] = {
                'estereotipo': estereotipo,
                'pais': pais,       # Lista de nomes das classes pai
                'pacote': pacote,
                'atributos': []     # Podemos preencher depois se precisarmos validar tipos
            }

    def adicionar_genset(self, nome, geral, especificas, modificadores):
        """Registra um conjunto de generalização."""
        self.gensets.append({
            'nome': nome,
            'geral': geral,             # A classe pai
            'especificas': especificas, # Lista de classes filhas
            'modificadores': modificadores # (disjoint, complete)
        })

class AnalisadorSemantico:
    def __init__(self, asts_globais):
        """
        asts_globais: Dicionário {'NomeArquivo': AST_Tupla} vindo do main.py
        """
        self.asts = asts_globais
        self.tabela = TabelaDeSimbolos()

    def analisar(self):
        print("\n" + "="*40)
        print("   INICIANDO ANÁLISE SEMÂNTICA")
        print("="*40)
        
        # Transformar as ASTs soltas em uma Tabela de Símbolos unificada
        self._construir_visao_de_mundo()
        
        if self.tabela.erros:
            self._imprimir_relatorio()
            return

        self._verificar_integridade_heranca()

        self._detectar_padroes_odp()

        self._imprimir_relatorio()

    def _construir_visao_de_mundo(self):
        """
        Varre todas as ASTs e preenche a tabela de símbolos
        """
        print("-> Construindo grafo de visão geral...")
        
        for nome_modulo, ast in self.asts.items():
            # Estrutura AST: ('programa', imports, pacote, declaracoes)
            # Indices: 0=tag, 1=imports, 2=pacote, 3=declaracoes
            
            pacote = ast[2][1] if ast[2] else "Desconhecido"
            declaracoes = ast[3]

            if not declaracoes:
                continue

            for decl in declaracoes:
                if not decl: continue
                tipo = decl[0]

                # Extração de Classes 
                if tipo.startswith('classe'):
                    self._processar_classe(decl, pacote)
                
                # Extração de Gensets
                elif tipo.startswith('genset'):
                    self._processar_genset(decl)

    def _processar_classe(self, decl, pacote):
        tipo = decl[0]
        nome = decl[2]
        estereotipo = decl[1]
        pais_str = None

        # Identifica onde está a lista de pais dependendo do tipo da tupla
        if tipo == 'classe_com_corpo_e_heranca':
            pais_str = decl[3]
        elif tipo in ['classe_subtipo_complexo_com_corpo', 'classe_subtipo_complexo']:
            pais_str = decl[4]
        elif tipo == 'classe_especializada_simples':
            pais_str = decl[3]
        
        lista_pais = [p.strip() for p in pais_str.split(',')] if pais_str else []
        self.tabela.adicionar_classe(nome, estereotipo, lista_pais, pacote)

    def _processar_genset(self, decl):
        
        if decl[0] == 'genset_completo':
            modificadores = decl[1]
            nome = decl[2]
            geral = decl[3]
            especificas = decl[4]
            
            self.tabela.adicionar_genset(nome, geral, especificas, modificadores)

    def _verificar_integridade_heranca(self):
        # Verifica se os pais citados nas heranças realmente existem
        print("-> Verificando integridade das referências...")

        for nome, dados in self.tabela.classes.items():
            for pai in dados['pais']:
                if pai not in self.tabela.classes:
                    # Se não achou a classe, mas o nome sugere algo conhecido, poderíamos tentar corrigir
                    # Por enquanto, apenas reportamos erro
                    self.tabela.erros.append(f"Erro de Integridade: Classe '{nome}' herda de '{pai}', mas '{pai}' não foi definida.")

    def _detectar_padroes_odp(self):
        """
        Aqui entra a lógica inteligente para detectar RoleMixin, Phase, Category, etc.
        """
        print("-> Buscando padrões de projeto (ODPs)...")
        # Vamos implementar a lógica do RoleMixin aqui na próxima etapa
        pass

    def _imprimir_relatorio(self):
        print("\n" + "="*40)
        print("          RELATÓRIO SEMÂNTICO")
        print("="*40)
        
        if self.tabela.erros:
            print("\n[ERROS ENCONTRADOS]")
            for i, erro in enumerate(self.tabela.erros, 1):
                print(f"{i}. {erro}")
        else:
            print("\n[SUCESSO] Nenhuma inconsistência estrutural básica encontrada.")

        if self.tabela.padroes_identificados:
            print("\n[PADRÕES IDENTIFICADOS]")
            for padrao in self.tabela.padroes_identificados:
                print(f"✅ {padrao}")
        else:
            print("\n[INFO] Nenhum padrão ODP completo foi identificado ainda.")