# semantic_analyzer/analyzer.py

class TabelaDeSimbolos:
    def __init__(self):
        self.classes = {} 
        self.gensets = []
        self.erros = []     
        self.padroes = []   
        self.coencoes = []  

    def adicionar_classe(self, nome, estereotipo, pais, pacote, mediacoes=[], caracterizacoes=[]):
        if nome not in self.classes:
            self.classes[nome] = {
                'estereotipo': estereotipo,
                'pais': pais,       
                'pacote': pacote,
                'filhos_diretos': [],
                'mediacoes': mediacoes,
                'caracterizacoes': caracterizacoes
            }

    def adicionar_genset(self, nome, geral, especificas, modificadores):
        self.gensets.append({
            'nome': nome,
            'geral': geral,
            'especificas': especificas,
            'modificadores': modificadores 
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
        print("\n" + "="*50)
        print("   INICIANDO ANÁLISE SEMÂNTICA")
        print("="*50)
        
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
                if tipo.startswith('classe'): self._extrair_classe(decl, pacote)
                elif tipo.startswith('genset'): self._extrair_genset(decl)

    def _extrair_classe(self, decl, pacote):
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
                
                # --- CORREÇÃO BASEADA NO DEBUG ---
                # Caso 1: Tupla de Link/Associação (Encontrada no Debug)
                # Formato: ('relacao_interna_tag_link', 'mediation', ('--', ...), '[1]', 'CarAgency')
                if item[0] == 'relacao_interna_tag_link':
                    tag = str(item[1])
                    # O alvo está no índice 4 nesta estrutura específica
                    tipo_alvo = item[4] if len(item) > 4 else "Desconhecido"
                    
                    # Verifica 'mediation' (com ou sem @)
                    if 'mediation' in tag:
                        lista_mediacoes.append(tipo_alvo)
                    elif 'characterization' in tag:
                        lista_caracterizacoes.append(tipo_alvo)

                # Caso 2: Tupla Genérica (Atributos comuns ou outras estruturas)
                elif isinstance(item, (tuple, list)):
                    flattened = [str(x) for x in item]
                    tipo_alvo = item[2] if len(item) > 2 else "Desconhecido"
                    
                    flat_str = " ".join(flattened)
                    if 'mediation' in flat_str: # Pega @mediation ou mediation
                        lista_mediacoes.append(tipo_alvo)
                    if 'characterization' in flat_str:
                        lista_caracterizacoes.append(tipo_alvo)

        self.tabela.adicionar_classe(nome, estereotipo, lista_pais, pacote, lista_mediacoes, lista_caracterizacoes)

    def _extrair_genset(self, decl):
        if decl[0] == 'genset_completo':
            self.tabela.adicionar_genset(decl[2], decl[3], decl[4], decl[1])
        elif decl[0] == 'genset_where':
            self.tabela.adicionar_genset(decl[2], decl[4], decl[3], decl[1])

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

    def _validar_genset(self, pai, filhos_esperados, tipo_filho_esperado):
        genset = next((g for g in self.tabela.gensets if g['geral'] == pai), None)
        if not genset:
            if len(filhos_esperados) > 0: return "Incompleto", f"Falta 'genset' para os filhos {filhos_esperados}."
            return "Ausente", "Sem filhos."
        
        mods = genset['modificadores']
        is_disjoint = False
        is_complete = False
        if isinstance(mods, tuple):
            if 'disjoint' in mods: is_disjoint = True
            if 'complete' in mods: is_complete = True
        elif isinstance(mods, str):
            if 'disjoint' in mods: is_disjoint = True
            if 'complete' in mods: is_complete = True
            if mods == 'disjoint_complete': is_disjoint = True; is_complete = True

        msgs = []
        if not is_disjoint: msgs.append("Falta disjoint")
        if not is_complete: msgs.append("Falta complete")
        
        for f in genset['especificas']:
            if f in self.tabela.classes:
                est = self.tabela.classes[f]['estereotipo']
                if tipo_filho_esperado != 'mixed' and est != tipo_filho_esperado:
                    msgs.append(f"Filho '{f}' é '{est}', esperava '{tipo_filho_esperado}'")
        
        if msgs: return "Incompleto", f"Problemas: {', '.join(msgs)}"
        return "Completo", f"Genset '{genset['nome']}' validado."

    def _detectar_mode_pattern(self):
        for nome, dados in self.tabela.classes.items():
            if dados['estereotipo'] == 'mode':
                caracterizacoes = dados['caracterizacoes']
                if not caracterizacoes:
                    self._registrar_padrao('Mode Pattern', nome, 'Incompleto', "Falta definir a relação de caracterização (@characterization).")
                    continue
                validos = [c for c in caracterizacoes if c in self.tabela.classes]
                if len(validos) == len(caracterizacoes):
                    self._registrar_padrao('Mode Pattern', nome, 'Completo', f"Caracteriza: {', '.join(caracterizacoes)}.")
                else:
                    self._registrar_padrao('Mode Pattern', nome, 'Incompleto', f"Refere-se a tipos desconhecidos: {set(caracterizacoes) - set(self.tabela.classes.keys())}")

    def _detectar_relator_pattern(self):
        for nome, dados in self.tabela.classes.items():
            if dados['estereotipo'] == 'relator':
                mediacoes = dados['mediacoes']
                if not mediacoes:
                    self._registrar_padrao('Relator Pattern', nome, 'Incompleto', "Falta definir as mediações (@mediation) no corpo.")
                    continue

                if len(mediacoes) < 2:
                    self._registrar_padrao('Relator Pattern', nome, 'Incompleto', f"Relator deve mediar ao menos 2 entidades. Encontrou: {mediacoes}")
                else:
                    validos = [m for m in mediacoes if m in self.tabela.classes]
                    if len(validos) == len(mediacoes):
                         self._registrar_padrao('Relator Pattern', nome, 'Completo', f"Relator conecta: {', '.join(mediacoes)}.")
                    else:
                        self._registrar_padrao('Relator Pattern', nome, 'Incompleto', f"Refere-se a tipos desconhecidos: {set(mediacoes) - set(self.tabela.classes.keys())}")

    def _detectar_subkind_pattern(self):
        for nome, dados in self.tabela.classes.items():
            if dados['estereotipo'] == 'subkind':
                pais = dados['pais']
                if not pais:
                    self._registrar_padrao('SubKind Pattern', nome, 'Incompleto', 'SubKind orfão.')
                    continue
                pai_valido = False
                nome_pai = None
                tipo_pai = None
                for pai in pais:
                    if pai in self.tabela.classes:
                        est_pai = self.tabela.classes[pai]['estereotipo']
                        if est_pai in self.RIGID_SORTALS:
                            pai_valido = True
                            nome_pai = pai
                            tipo_pai = est_pai
                            break
                if pai_valido:
                    self._registrar_padrao('SubKind Pattern', nome, 'Completo', f"Especializa '{nome_pai}' ({tipo_pai}).")
                else:
                    self._registrar_padrao('SubKind Pattern', nome, 'Incompleto', f"Pai inválido {pais}.")

    def _detectar_phase_pattern(self):
        permitidos_pai = self.RIGID_SORTALS + ['phase']
        for nome_pai, dados_pai in self.tabela.classes.items():
            if dados_pai['estereotipo'] in permitidos_pai:
                filhos_phase = [f for f in dados_pai['filhos_diretos'] 
                                if self.tabela.classes.get(f, {}).get('estereotipo') == 'phase']
                if filhos_phase:
                    status, msg = self._validar_genset(nome_pai, filhos_phase, 'phase')
                    self._registrar_padrao('Phase Pattern', nome_pai, status, msg)

    def _detectar_role_pattern(self):
        permitidos_pai = self.RIGID_SORTALS + ['role', 'roleMixin']
        for nome, dados in self.tabela.classes.items():
            if dados['estereotipo'] == 'role':
                pais = dados['pais']
                tem_pai_rolemixin = False
                for pai in pais:
                    if self.tabela.classes.get(pai, {}).get('estereotipo') == 'roleMixin':
                        tem_pai_rolemixin = True
                if tem_pai_rolemixin: continue 
                
                if not pais:
                    self._registrar_padrao('Role Pattern', nome, 'Incompleto', 'Role sem pai.')
                    continue

                pai_valido = False
                nome_pai = None
                tipo_pai = None
                for pai in pais:
                    if pai in self.tabela.classes:
                        est_pai = self.tabela.classes[pai]['estereotipo']
                        if est_pai in permitidos_pai:
                            pai_valido = True
                            nome_pai = pai
                            tipo_pai = est_pai
                            break
                if pai_valido:
                    self._registrar_padrao('Role Pattern', nome, 'Completo', f"Especializa '{nome_pai}' ({tipo_pai}).")
                else:
                    self._registrar_padrao('Role Pattern', nome, 'Incompleto', f"Pai inválido {pais}.")

    def _detectar_rolemixin_pattern(self):
        for nome, dados in self.tabela.classes.items():
            if dados['estereotipo'] == 'roleMixin':
                filhos_role = [f for f in dados['filhos_diretos'] 
                               if self.tabela.classes.get(f, {}).get('estereotipo') == 'role']
                status, msg = self._validar_genset(nome, filhos_role, 'role')
                self._registrar_padrao('RoleMixin Pattern', nome, status, msg)

    def _detectar_category_pattern(self):
        for nome, dados in self.tabela.classes.items():
            if dados['estereotipo'] == 'category':
                genset = next((g for g in self.tabela.gensets if g['geral'] == nome), None)
                if genset:
                    filhos_ok = True
                    for f in genset['especificas']:
                        if f in self.tabela.classes:
                            if self.tabela.classes[f]['estereotipo'] not in self.RIGID_SORTALS:
                                filhos_ok = False
                    status, msg = self._validar_genset(nome, [], 'mixed')
                    if not filhos_ok: status = "Incompleto"; msg += " (Filhos não rígidos)."
                    self._registrar_padrao('Category Pattern', nome, status, msg)
                else:
                    self._registrar_padrao('Category Pattern', nome, 'Incompleto', 'Falta genset.')

    def _registrar_padrao(self, tipo, classe, status, msg):
        self.tabela.padroes.append({'tipo': tipo, 'classe': classe, 'status': status, 'msg': msg})

    def _imprimir_relatorio(self):
        if not self.tabela.padroes and not self.tabela.erros and not self.tabela.coencoes:
            print("\n[INFO] Nenhuma estrutura ODP reconhecível encontrada.")
            return

        if self.tabela.coencoes:
            print("\n🔧 COERÇÕES / CORREÇÕES AUTOMÁTICAS APLICADAS:")
            for c in self.tabela.coencoes:
                print(f"   - {c}")

        print("\n✅ PADRÕES COMPLETOS IDENTIFICADOS:")
        for p in [x for x in self.tabela.padroes if x['status'] == 'Completo']:
            print(f"   - [{p['tipo']}] em '{p['classe']}': {p['msg']}")

        print("\n⚠️  PADRÕES INCOMPLETOS:")
        for p in [x for x in self.tabela.padroes if x['status'] == 'Incompleto']:
            print(f"   - [{p['tipo']}] em '{p['classe']}': {p['msg']}")
        
        if self.tabela.erros:
            print("\n❌ ERROS ESTRUTURAIS FATAIS:")
            for e in self.tabela.erros:
                print(f"   - {e}")