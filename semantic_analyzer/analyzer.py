# semantic_analyzer/analyzer.py
import re
from tabulate import tabulate

class TabelaDeSimbolos:
    def __init__(self):
        self.classes = {} 
        self.gensets = []
        self.materiais = [] 
        self.erros = []     
        self.padroes = []   
        self.coencoes = []  

    def adicionar_classe(self, nome, estereotipo, pais, pacote, mediacoes=[], caracterizacoes=[], arquivo="?", linha=0):
        if nome not in self.classes:
            self.classes[nome] = {
                'estereotipo': estereotipo,
                'pais': pais,       
                'pacote': pacote,
                'filhos_diretos': [],
                'mediacoes': mediacoes,
                'caracterizacoes': caracterizacoes,
                'arquivo': arquivo,
                'linha': linha
            }

    def adicionar_genset(self, nome, geral, especificas, modificadores, arquivo="?", linha=0):
        self.gensets.append({
            'nome': nome,
            'geral': geral,
            'especificas': especificas,
            'modificadores': modificadores,
            'arquivo': arquivo,
            'linha': linha
        })
    
    def adicionar_material(self, origem, destino):
        self.materiais.append({
            'origem': origem,
            'destino': destino
        })

    def processar_hierarquia(self):
        for nome_filho, dados in self.classes.items():
            for pai in dados['pais']:
                if pai in self.classes:
                    self.classes[pai]['filhos_diretos'].append(nome_filho)

class AnalisadorSemantico:
    # Taxonomia UFO
    IDENTITY_PROVIDERS = ['kind', 'collective', 'quantity', 'relator', 'mode', 'quality']
    RIGID_SORTALS = IDENTITY_PROVIDERS + ['subkind']
    ANTI_RIGID_SORTALS = ['role', 'phase']
    MIXINS = ['category', 'roleMixin', 'phaseMixin', 'mixin']

    def __init__(self, asts_globais):
        self.asts = asts_globais
        self.tabela = TabelaDeSimbolos()

    def analisar(self):
        print("\n" + "/"*60)
        print("                INICIANDO ANÁLISE SEMÂNTICA")
        print("/"*60)
        
        self._construir_visao_de_mundo()
        self.tabela.processar_hierarquia()
        self._aplicar_coercao_de_erros()

        self._detectar_subkind_pattern()
        self._detectar_phase_pattern()
        self._detectar_role_pattern()
        self._detectar_rolemixin_pattern()
        self._detectar_category_pattern()
        self._detectar_relator_pattern()
        self._detectar_mode_pattern()
        
        self._imprimir_relatorio()

    def _construir_visao_de_mundo(self):
        for nome_modulo, ast in self.asts.items():
            pacote = ast[2][1] if ast[2] else "Desconhecido"
            declaracoes = ast[3]
            if not declaracoes: continue
            for decl in declaracoes:
                if not decl: continue
                tipo = decl[0]
                
                if tipo.startswith('classe'): 
                    self._extrair_classe(decl, pacote)
                elif tipo.startswith('genset'): 
                    self._extrair_genset(decl)
                elif 'relacao' in tipo or 'link' in tipo:
                    self._extrair_relacao(decl)

    def _extrair_classe(self, decl, pacote):
        arquivo = decl[-2] if len(decl) >= 2 else "?"
        linha = decl[-1] if len(decl) >= 1 else 0
        
        tipo_tupla = decl[0]
        estereotipo = decl[1]
        nome = decl[2]
        pais_obj = None
        corpo = []

        if tipo_tupla == 'classe_com_corpo_e_heranca':
            pais_obj = decl[3]; corpo = decl[4]
        elif tipo_tupla == 'classe_subtipo_complexo_com_corpo':
            pais_obj = decl[4]; corpo = decl[5]
        elif tipo_tupla == 'classe_especializada_simples':
            pais_obj = decl[3]
        elif tipo_tupla == 'classe_subtipo_complexo':
            pais_obj = decl[4]
        elif tipo_tupla == 'classe_com_corpo':
            corpo = decl[3]
        
        lista_pais = []
        if isinstance(pais_obj, list): lista_pais = pais_obj
        elif isinstance(pais_obj, str): lista_pais = [p.strip() for p in pais_obj.split(',')]

        lista_mediacoes = []
        lista_caracterizacoes = []

        if corpo:
            for item in corpo:
                if not item: continue
                if isinstance(item, (tuple, list)):
                    def flatten(x):
                        if isinstance(x, (list, tuple)): return [a for i in x for a in flatten(i)]
                        else: return [str(x)]
                    flattened = flatten(item)
                    flat_str = " ".join(flattened)
                    
                    tipo_alvo = "Desconhecido"
                    tag = item[0]
                    
                    if tag == 'relacao_interna_padrao': 
                        if len(item) > 5: tipo_alvo = item[5]
                    elif tag == 'relacao_interna_tag_link':
                        if len(item) > 4: tipo_alvo = item[4]
                    elif tag == 'relacao_interna_link_simples':
                        if len(item) > 3: tipo_alvo = item[3]
                    elif tag == 'relacao_interna_link_duplo':
                        if len(item) > 4: tipo_alvo = item[4]
                    elif tag == 'relacao_interna_tag_link_duplo':
                        if len(item) > 5: tipo_alvo = item[5]
                    elif tag == 'relacao_interna_sem_tag':
                        if len(item) > 4: tipo_alvo = item[4]
                    else:
                        if len(item) > 2: tipo_alvo = item[2]

                    if 'mediation' in flat_str:
                        lista_mediacoes.append(tipo_alvo)
                    if 'characterization' in flat_str:
                        lista_caracterizacoes.append(tipo_alvo)

        self.tabela.adicionar_classe(nome, estereotipo, lista_pais, pacote, lista_mediacoes, lista_caracterizacoes, arquivo, linha)

    def _extrair_genset(self, decl):
        arquivo = decl[-2] if len(decl) >= 2 else "?"
        linha = decl[-1] if len(decl) >= 1 else 0
        
        if decl[0] == 'genset_completo':
            self.tabela.adicionar_genset(decl[2], decl[3], decl[4], decl[1], arquivo, linha)
        elif decl[0] == 'genset_where':
            self.tabela.adicionar_genset(decl[2], decl[4], decl[3], decl[1], arquivo, linha)

    def _extrair_relacao(self, decl):
        # --- CORREÇÃO AQUI: Lógica exata baseada nos índices do Sintático ---
        tag = decl[0]
        
        # Verifica se é uma relação material olhando o estereótipo (índice 1)
        if len(decl) > 1 and decl[1] == 'material':
            try:
                # O parser sintático gera tuplas onde:
                # decl[2] é a classe Origem
                # decl[6] é a classe Destino (seja link simples ou link nomeado)
                # Exemplo: ('relacao_externa_link', 'material', 'Paciente', '[1..*]', (...), '[1..*]', 'Medico', ...)
                
                if tag in ['relacao_externa', 'relacao_externa_link']:
                    origem = decl[2]
                    destino = decl[6] 
                    self.tabela.adicionar_material(origem, destino)
            except:
                pass

    def _aplicar_coercao_de_erros(self):
        for nome, dados in self.tabela.classes.items():
            est_atual = dados['estereotipo']
            pais = dados['pais']
            if est_atual == 'kind' and pais:
                dados['estereotipo'] = 'subkind'
                self.tabela.coencoes.append(f"Classe '{nome}' era 'kind' mas tem pais. Coagida para 'subkind'.")
                continue
            if est_atual == 'subkind' and pais:
                pai_anti_rigido = None
                for p in pais:
                    if p in self.tabela.classes:
                        if self.tabela.classes[p]['estereotipo'] in self.ANTI_RIGID_SORTALS:
                            pai_anti_rigido = self.tabela.classes[p]['estereotipo']
                            break
                if pai_anti_rigido:
                    dados['estereotipo'] = pai_anti_rigido
                    self.tabela.coencoes.append(f"Classe '{nome}' (subkind) herda de '{pai_anti_rigido}'. Coagida para '{pai_anti_rigido}'.")

    def _validar_genset_flex(self, pai, filhos_esperados, disjoint_obrigatorio=False, complete_obrigatorio=False):
        genset_encontrado = None
        filho_alvo_busca = filhos_esperados[0] if filhos_esperados else None

        for g in self.tabela.gensets:
            if g['geral'] == pai:
                if filho_alvo_busca:
                    if filho_alvo_busca in g['especificas']:
                        genset_encontrado = g
                        break
                else:
                    genset_encontrado = g
                    break
        
        if not genset_encontrado:
            if filhos_esperados:
                lista_filhos = ", ".join(filhos_esperados)
                return "Incompleto", f"Falta um 'genset' do pai '{pai}' que agrupe: [{lista_filhos}]."
            return "Ausente", "Sem filhos."
        
        mods = genset_encontrado['modificadores']
        tokens_mods = []
        if isinstance(mods, str):
            clean_str = mods.replace(',', ' ').replace(';', ' ')
            tokens_mods = clean_str.split()
        elif isinstance(mods, (list, tuple)):
            tokens_mods = [str(m).strip() for m in mods]
        
        is_disjoint = 'disjoint' in tokens_mods
        is_complete = 'complete' in tokens_mods
        
        msgs = []
        aviso = ""
        
        if disjoint_obrigatorio and not is_disjoint:
            msgs.append("Falta 'disjoint' (Obrigatório)")
        
        if complete_obrigatorio and not is_complete:
            msgs.append("Falta 'complete' (Obrigatório)")

        if not disjoint_obrigatorio and is_disjoint and 'role' in str(filhos_esperados):
            aviso = " (Nota: 'disjoint' não se aplica semanticamente a roles, mas o genset existe)."

        if msgs: return "Incompleto", f"Problemas: {', '.join(msgs)}"
        return "Completo", f"Genset '{genset_encontrado['nome']}' validado.{aviso}"

    def _detectar_mode_pattern(self):
        for nome, dados in self.tabela.classes.items():
            if dados['estereotipo'] == 'mode':
                caracterizacoes = dados['caracterizacoes']
                if not caracterizacoes:
                    self._registrar_padrao('Mode Pattern', nome, 'Incompleto', "Falta definir a relação de caracterização (@characterization).")
                    continue
                erros_tipo = []
                for alvo in caracterizacoes:
                    if alvo in self.tabela.classes:
                        est_alvo = self.tabela.classes[alvo]['estereotipo']
                        if est_alvo != 'kind':
                            erros_tipo.append(f"'{alvo}' é '{est_alvo}' (Esperado: 'kind')")
                    else: erros_tipo.append(f"'{alvo}' não encontrado")
                if erros_tipo:
                    self._registrar_padrao('Mode Pattern', nome, 'Incompleto', f"Erro de Tipagem no alvo: {', '.join(erros_tipo)}")
                else:
                    self._registrar_padrao('Mode Pattern', nome, 'Completo', f"Caracteriza corretamente kinds: {', '.join(caracterizacoes)}.")

    def _detectar_relator_pattern(self):
        for nome, dados in self.tabela.classes.items():
            if dados['estereotipo'] == 'relator':
                mediacoes = dados['mediacoes']
                if not mediacoes:
                    self._registrar_padrao('Relator Pattern', nome, 'Incompleto', "Falta definir as mediações (@mediation) no corpo.")
                    continue
                tem_material = False
                for mat in self.tabela.materiais:
                    if mat['origem'] in mediacoes and mat['destino'] in mediacoes:
                        tem_material = True; break
                if not tem_material:
                     self._registrar_padrao('Relator Pattern', nome, 'Incompleto', f"Mediações ok {mediacoes}, mas falta a relação externa '@material' conectando esses papéis.")
                else:
                     self._registrar_padrao('Relator Pattern', nome, 'Completo', f"Relator conecta {mediacoes} e possui relação @material correspondente.")

    def _detectar_subkind_pattern(self):
        for nome, dados in self.tabela.classes.items():
            if dados['estereotipo'] == 'subkind':
                pais = dados['pais']
                if not pais: continue 
                
                pai_rigido = None
                for p in pais:
                    if p in self.tabela.classes and self.tabela.classes[p]['estereotipo'] in self.RIGID_SORTALS:
                        pai_rigido = p; break
                if not pai_rigido:
                    self._registrar_padrao('SubKind Pattern', nome, 'Incompleto', f"Pai inválido.")
                    continue
                
                irmaos_subkind = [f for f in self.tabela.classes[pai_rigido]['filhos_diretos'] 
                                  if self.tabela.classes.get(f, {}).get('estereotipo') == 'subkind']
                
                if len(irmaos_subkind) == 1:
                    self._registrar_padrao('SubKind Pattern', nome, 'Completo', f"Especializa '{pai_rigido}'. Filho único, genset dispensado.")
                else:
                    status, msg = self._validar_genset_flex(pai_rigido, [nome], disjoint_obrigatorio=True, complete_obrigatorio=False)
                    if status == 'Incompleto':
                        msg += f" (Irmãos encontrados: {', '.join(irmaos_subkind)})"
                    self._registrar_padrao('SubKind Pattern', nome, status, msg)

    def _detectar_phase_pattern(self):
        permitidos_pai = self.RIGID_SORTALS + ['phase']
        for nome_pai, dados_pai in self.tabela.classes.items():
            if dados_pai['estereotipo'] in permitidos_pai:
                filhos_phase = [f for f in dados_pai['filhos_diretos'] 
                                if self.tabela.classes.get(f, {}).get('estereotipo') == 'phase']
                if filhos_phase:
                    status, msg = self._validar_genset_flex(nome_pai, filhos_phase, disjoint_obrigatorio=True, complete_obrigatorio=False)
                    self._registrar_padrao('Phase Pattern', nome_pai, status, msg)

    def _detectar_role_pattern(self):
        permitidos_pai = self.RIGID_SORTALS + ['role', 'roleMixin', 'phase']
        for nome, dados in self.tabela.classes.items():
            if dados['estereotipo'] == 'role':
                pais = dados['pais']
                if not pais: continue
                pai_valido = None
                for p in pais:
                    if p in self.tabela.classes:
                         est_p = self.tabela.classes[p]['estereotipo']
                         if est_p in permitidos_pai: pai_valido = p; break
                if not pai_valido:
                     self._registrar_padrao('Role Pattern', nome, 'Incompleto', f"Pai inválido.")
                     continue
                
                irmaos_role = [f for f in self.tabela.classes[pai_valido]['filhos_diretos'] 
                               if self.tabela.classes.get(f, {}).get('estereotipo') == 'role']

                if len(irmaos_role) == 1:
                    self._registrar_padrao('Role Pattern', nome, 'Completo', f"Especializa '{pai_valido}'. Filho único, genset dispensado.")
                else:
                    status, msg = self._validar_genset_flex(pai_valido, [nome], disjoint_obrigatorio=False, complete_obrigatorio=False)
                    if status == 'Incompleto':
                        msg += f" (Irmãos encontrados: {', '.join(irmaos_role)})"
                    self._registrar_padrao('Role Pattern', nome, status, msg)

    def _detectar_rolemixin_pattern(self):
        for nome, dados in self.tabela.classes.items():
            if dados['estereotipo'] == 'roleMixin':
                filhos_role = [f for f in dados['filhos_diretos'] 
                               if self.tabela.classes.get(f, {}).get('estereotipo') == 'role']
                
                if len(filhos_role) == 1:
                    self._registrar_padrao('RoleMixin Pattern', nome, 'Completo', f"RoleMixin com filho único '{filhos_role[0]}', genset dispensado.")
                else:
                    status, msg = self._validar_genset_flex(nome, filhos_role, disjoint_obrigatorio=True, complete_obrigatorio=True)
                    if status == 'Incompleto':
                        msg += f" (Irmãos encontrados: {', '.join(filhos_role)})"
                    self._registrar_padrao('RoleMixin Pattern', nome, status, msg)

    def _detectar_category_pattern(self):
        for nome, dados in self.tabela.classes.items():
            if dados['estereotipo'] == 'category':
                status, msg = self._validar_genset_flex(nome, [], disjoint_obrigatorio=False, complete_obrigatorio=False)
                self._registrar_padrao('Category Pattern', nome, status, msg)

    def _registrar_padrao(self, tipo, classe, status, msg):
        dados = self.tabela.classes.get(classe, {})
        linha = dados.get('linha', '?')
        arquivo = dados.get('arquivo', '?')
        self.tabela.padroes.append({
            'tipo': tipo, 
            'classe': classe, 
            'status': status, 
            'msg': msg, 
            'linha': linha,
            'arquivo': arquivo
        })

    def _imprimir_relatorio(self):
        if not self.tabela.padroes and not self.tabela.erros and not self.tabela.coencoes:
            print("\n[INFO] Nenhuma estrutura ODP reconhecível encontrada.")
            return

        headers = ["Padrão", "Detalhes", "Arquivo", "Linha"]
        rows_complete = []
        rows_incomplete = []

        for p in self.tabela.padroes:
            detalhes = f"'{p['classe']}': {p['msg']}"
            row = [p['tipo'], detalhes, p['arquivo'], p['linha']]

            if p['status'] == 'Completo':
                rows_complete.append(row)
            else:
                rows_incomplete.append(row)

        print("\n✅ PADRÕES COMPLETOS IDENTIFICADOS:")
        print(tabulate(rows_complete, headers=headers, tablefmt="grid"))

        print("\n⚠️  PADRÕES INCOMPLETOS:")
        print(tabulate(rows_incomplete, headers=headers, tablefmt="grid"))
        