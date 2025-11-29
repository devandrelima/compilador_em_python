import ply.yacc as yacc
import os  
from lexico_analyzer.lexer_puro import tokens, lexer
from tabulate import tabulate

erros_sintaticos = []

def p_programa(p):
    'programa : lista_imports_opt declaracao_pacote lista_declaracoes_opt'
    p[0] = ('programa', p[1], p[2], p[3])

def p_lista_imports_opt(p):
    '''lista_imports_opt : lista_imports
                         | empty'''
    p[0] = p[1]

def p_lista_imports(p):
    '''lista_imports : declaracao_import lista_imports
                     | declaracao_import'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_declaracao_import(p):
    'declaracao_import : import CLASS_ID'
    p[0] = ('import', p[2])

def p_lista_declaracoes_opt(p):
    '''lista_declaracoes_opt : lista_declaracoes
                             | empty'''
    p[0] = p[1]

def p_lista_declaracoes(p):
    '''lista_declaracoes : declaracao lista_declaracoes
                         | declaracao'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2] 
    else:
        p[0] = [p[1]] 

def p_declaracao(p):
    '''declaracao : declaracao_classe
                  | declaracao_tipo_dado
                  | declaracao_enum
                  | declaracao_genset
                  | declaracao_relacao_externa'''
    p[0] = p[1]

def p_declaracao_pacote(p):
    'declaracao_pacote : package CLASS_ID'
    p[0] = ('pacote', p[2])

def p_declaracao_classe(p):
    """declaracao_classe : estereotipo_classe CLASS_ID '{' corpo_classe '}'
                         | estereotipo_classe CLASS_ID specializes lista_ids
                         | estereotipo_classe CLASS_ID specializes lista_ids '{' corpo_classe '}'
                         | estereotipo_subtipo CLASS_ID specializes lista_ids
                         | estereotipo_subtipo CLASS_ID specializes lista_ids '{' corpo_classe '}'
                         | estereotipo_subtipo CLASS_ID of estereotipo_complexo specializes lista_ids
                         | estereotipo_subtipo CLASS_ID of estereotipo_complexo specializes lista_ids '{' corpo_classe '}'
                         | estereotipo_classe CLASS_ID of estereotipo_complexo
                         | estereotipo_classe CLASS_ID of estereotipo_complexo '{' corpo_classe '}'
                         | estereotipo_classe CLASS_ID
                         | estereotipo_subtipo CLASS_ID""" 
    
    if len(p) == 9: 
        p[0] = ('classe_subtipo_complexo_com_corpo', p[1], p[2], p[4], p[6], p[8])
    elif len(p) == 8: 
        p[0] = ('classe_com_corpo_e_heranca', p[1], p[2], p[4], p[6])
    elif len(p) == 7: 
        p[0] = ('classe_subtipo_complexo', p[1], p[2], p[4], p[6])
    elif len(p) == 6:
        if p[3] == 'of':
             p[0] = ('classe_complexa_com_corpo', p[1], p[2], p[4], p[5])
        else:
             p[0] = ('classe_com_corpo', p[1], p[2], p[4])
    elif len(p) == 5:
        if p[3] == 'of':
             p[0] = ('classe_complexa_simples', p[1], p[2], p[4])
        else:
             p[0] = ('classe_especializada_simples', p[1], p[2], p[4]) 
    else:
        p[0] = ('classe_simples', p[1], p[2])

def p_estereotipo_subtipo(p):
    '''estereotipo_subtipo : subkind
                           | phase
                           | role'''
    p[0] = p[1]

def p_estereotipo_complexo(p):
    '''estereotipo_complexo : functional_complexes
                            | relators
                            | intrinsic_modes
                            | collectives'''
    p[0] = p[1]

def p_class_ref(p):
    '''class_ref : CLASS_ID
                 | CLASS_ID '.' CLASS_ID'''
    if len(p) == 4:
        p[0] = f"{p[1]}.{p[3]}"
    else:
        p[0] = p[1]

def p_lista_ids(p):
    """lista_ids : class_ref ',' lista_ids
                 | class_ref"""
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

def p_corpo_classe(p):
    '''corpo_classe : lista_membros_classe
                    | empty'''
    p[0] = p[1]

def p_lista_membros_classe(p):
    '''lista_membros_classe : membro_classe lista_membros_classe
                            | membro_classe'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_membro_classe(p):
    '''membro_classe : declaracao_atributo
                     | declaracao_relacao_interna'''
    p[0] = p[1]

def p_cardinality_opt(p):
    '''cardinality_opt : CARDINALITY
                       | empty'''
    p[0] = p[1]

def p_declaracao_atributo(p):
    '''declaracao_atributo : RELATION_ID ':' tipo cardinality_opt meta_atributos_opt
                           | number ':' tipo cardinality_opt meta_atributos_opt
                           | string ':' tipo cardinality_opt meta_atributos_opt
                           | boolean ':' tipo cardinality_opt meta_atributos_opt
                           | date ':' tipo cardinality_opt meta_atributos_opt
                           | time ':' tipo cardinality_opt meta_atributos_opt
                           | datetime ':' tipo cardinality_opt meta_atributos_opt'''
    p[0] = ('atributo', p[1], p[3], p[4], p[5])

def p_tipo(p):
    '''tipo : dado_nativo
            | NEW_TYPE
            | CLASS_ID
            | CLASS_ID '.' CLASS_ID'''
    if len(p) == 4:
        p[0] = f"{p[1]}.{p[3]}"
    else:
        p[0] = p[1] 

def p_meta_atributos_opt(p):
    """meta_atributos_opt : '{' lista_meta_atributos '}'
                          | empty"""
    p[0] = p[2] if len(p) == 4 else None

def p_lista_meta_atributos(p):
    '''lista_meta_atributos : const
                            | ordered
                            | derived
                            | subsets
                            | redefines'''
    p[0] = p[1]

def p_declaracao_tipo_dado(p):
    """declaracao_tipo_dado : datatype NEW_TYPE '{' corpo_classe '}'
                            | datatype NEW_TYPE specializes lista_ids
                            | datatype NEW_TYPE specializes dado_nativo"""
    
    if len(p) == 6: 
        p[0] = ('datatype', p[2], p[4])
    elif len(p) == 5: # Com especialização
        pais = p[4]
        if isinstance(pais, list):
            pais = ", ".join(pais)
        p[0] = ('datatype_specialized', p[2], pais)

def p_declaracao_enum(p):
    "declaracao_enum : enum CLASS_ID '{' lista_instancias_enum '}'"
    p[0] = ('enum', p[2], p[4]) 

def p_lista_instancias_enum(p):
    """lista_instancias_enum : INSTANCE_ID ',' lista_instancias_enum
                             | INSTANCE_ID"""
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

def p_declaracao_genset(p):
    """declaracao_genset : genset_modifiers_opt genset CLASS_ID where lista_classes_genset specializes CLASS_ID
                         | genset_modifiers_opt genset CLASS_ID '{' genset_corpo '}'
                         | genset_modifiers_opt genset '{' genset_corpo '}'
                         | genset genset_modifiers_opt CLASS_ID '{' genset_corpo '}'
                         | genset genset_modifiers_opt '{' genset_corpo '}'
                         | genset genset_modifiers_opt CLASS_ID where lista_classes_genset specializes CLASS_ID"""
    
    modifiers = None
    name = "Anônimo"
    general = None
    specifics = []

    if len(p) == 8:
        if p[1] == 'genset': 
             modifiers = p[2]
             name = p[3]
             specifics = p[5]
             general = p[7]
        else:
             modifiers = p[1]
             name = p[3]
             specifics = p[5]
             general = p[7]
        p[0] = ('genset_where', modifiers, name, specifics, general)
    
    elif len(p) == 7:
        if p[2] == 'genset':
            modifiers = p[1]
            name = p[3]
            body = p[5]
        else:
            modifiers = p[2]
            name = p[3]
            body = p[5]
        
        if body:
            general = body[1]
            specifics = body[2]
        
        p[0] = ('genset_completo', modifiers, name, general, specifics)

    elif len(p) == 6:
        if p[2] == 'genset':
            modifiers = p[1]
            body = p[4]
        else:
            modifiers = p[2]
            body = p[4]
        
        if body:
            general = body[1]
            specifics = body[2]

        p[0] = ('genset_completo', modifiers, name, general, specifics)

def p_genset_modifiers_opt(p):
    '''genset_modifiers_opt : disjoint complete 
                            | disjoint_complete
                            | disjoint
                            | complete
                            | empty'''
    if len(p) == 3: 
        p[0] = (p[1], p[2])
    elif len(p) == 2:
        if p[1] == 'disjoint_complete':
            p[0] = ('disjoint', 'complete')
        else:
            p[0] = p[1]
    else:
        p[0] = None

def p_lista_classes_genset(p):
    """lista_classes_genset : CLASS_ID ',' lista_classes_genset
                            | CLASS_ID"""
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

def p_genset_corpo(p):
    'genset_corpo : general CLASS_ID specifics lista_classes_genset'
    p[0] = ('corpo_genset', p[2], p[4])

def p_inverse_opt(p):
    '''inverse_opt : inverseOf CLASS_ID '.' RELATION_ID
                   | inverseOf CLASS_ID
                   | empty'''
    if len(p) == 5:
        p[0] = f"{p[2]}.{p[4]}"
    elif len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = None

def p_id_dot_ref(p):
    '''id_dot_ref : CLASS_ID '.' RELATION_ID
                  | CLASS_ID'''
    if len(p) == 4:
        p[0] = f"{p[1]}.{p[3]}"
    else:
        p[0] = p[1]

def p_relation_constraint_opt(p):
    '''relation_constraint_opt : '(' '{' subsets id_dot_ref '}' ')'
                               | '(' '{' redefines id_dot_ref '}' ')'
                               | '(' '{' const '}' ')'
                               | empty'''
    if len(p) == 7: 
        p[0] = f"{{{p[3]} {p[4]}}}"
    elif len(p) == 6: 
        p[0] = f"{{{p[3]}}}"
    else:
        p[0] = None

def p_declaracao_relacao_interna(p):
    """declaracao_relacao_interna : '@' estereotipo_relacao CARDINALITY simbolo_associacao CARDINALITY class_ref inverse_opt
                                  | '@' estereotipo_relacao link_nomeado CARDINALITY class_ref inverse_opt
                                  | link_nomeado CARDINALITY class_ref inverse_opt
                                  | CARDINALITY link_nomeado CARDINALITY class_ref inverse_opt
                                  | '@' estereotipo_relacao CARDINALITY link_nomeado CARDINALITY class_ref inverse_opt
                                  | CARDINALITY simbolo_associacao CARDINALITY class_ref inverse_opt"""
    
    # Caso 1: @stereo [1] -- [1] Class (7 elementos)
    if len(p) == 8 and p[1] == '@':
        p[0] = ('relacao_interna_padrao', p[2], p[3], p[4], p[5], p[6])

    # Caso 2: @stereo --link-- [1] Class (7 elementos - Link Nomeado)
    # Atenção: p[3] é o link (tupla)
    elif len(p) == 7 and p[1] == '@' and isinstance(p[3], tuple):
         p[0] = ('relacao_interna_tag_link', p[2], p[3], p[4], p[5])
    
    # Caso 3: --link-- [1] Class (5 elementos)
    # Não tem @, não tem card inicial.
    elif len(p) == 5 and isinstance(p[1], tuple):
         p[0] = ('relacao_interna_link_simples', p[1], p[2], p[3])

    # Caso 4: [1] --link-- [1] Class (6 elementos)
    elif len(p) == 6 and isinstance(p[2], tuple):
         p[0] = ('relacao_interna_link_duplo', p[1], p[2], p[3], p[4])
    
    # Caso 5: @stereo [1] --link-- [1] Class (8 elementos)
    elif len(p) == 8 and p[1] == '@' and isinstance(p[4], tuple):
        p[0] = ('relacao_interna_tag_link_duplo', p[2], p[3], p[4], p[5], p[6])

    # Caso 6: [1] -- [1] Class (6 elementos - Simbolo normal)
    elif len(p) == 6:
         p[0] = ('relacao_interna_sem_tag', p[1], p[2], p[3], p[4])
    
    else:
        # Fallback seguro
        p[0] = ('relacao_desconhecida',)
        
def p_link_nomeado(p):
    '''link_nomeado : ASSOCIATION RELATION_ID ASSOCIATION
                    | COMPOSITION_L RELATION_ID ASSOCIATION
                    | COMPOSITION_R RELATION_ID ASSOCIATION
                    | COMPOSITION_LO RELATION_ID ASSOCIATION
                    | COMPOSITION_RO RELATION_ID ASSOCIATION
                    | ASSOCIATION RELATION_ID COMPOSITION_R
                    | ASSOCIATION RELATION_ID COMPOSITION_RO
                    | ASSOCIATION RELATION_ID COMPOSITION_L
                    | ASSOCIATION RELATION_ID COMPOSITION_LO'''
    p[0] = (p[1], p[2], p[3]) 

def p_specializes_rel_opt(p):
    '''specializes_rel_opt : specializes CLASS_ID '.' RELATION_ID
                           | specializes CLASS_ID
                           | empty'''
    if len(p) == 5:
        p[0] = f"{p[2]}.{p[4]}"
    elif len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = None

def p_declaracao_relacao_externa(p):
    """declaracao_relacao_externa : '@' estereotipo_relacao relation CLASS_ID CARDINALITY simbolo_associacao CARDINALITY CLASS_ID specializes_rel_opt
                                  | relation CLASS_ID CARDINALITY simbolo_associacao CARDINALITY CLASS_ID specializes_rel_opt
                                  | relation CLASS_ID CARDINALITY link_nomeado CARDINALITY CLASS_ID specializes_rel_opt
                                  | '@' estereotipo_relacao relation CLASS_ID CARDINALITY link_nomeado CARDINALITY CLASS_ID specializes_rel_opt"""
    
    if len(p) == 10:
        if isinstance(p[6], tuple):
             p[0] = ('relacao_externa_link', p[2], p[4], p[5], p[6], p[7], p[8], p[9])
        else:
             p[0] = ('relacao_externa', p[2], p[4], p[5], p[6], p[7], p[8], p[9])

    elif len(p) == 8:
        if isinstance(p[4], tuple):
            p[0] = ('relacao_externa_sem_tag_link', "relation", p[2], p[3], p[4], p[5], p[6], p[7])
        else:
            p[0] = ('relacao_externa_sem_tag', "relation", p[2], p[3], p[4], p[5], p[6], p[7])

def p_simbolo_associacao(p):
    '''simbolo_associacao : ASSOCIATION
                          | COMPOSITION_L
                          | COMPOSITION_R
                          | COMPOSITION_LO
                          | COMPOSITION_RO'''
    p[0] = p[1]

def p_estereotipo_classe(p):
    '''estereotipo_classe : event
                          | situation
                          | process
                          | category
                          | mixin
                          | phaseMixin
                          | roleMixin
                          | historicalRoleMixin
                          | kind
                          | collective
                          | quantity
                          | quality
                          | mode
                          | intrinsicMode     
                          | extrinsicMode
                          | historicalRole
                          | relator
                          | type'''
    p[0] = p[1]

def p_estereotipo_relacao(p):
    '''estereotipo_relacao : material
                           | derivation
                           | comparative
                           | mediation
                           | characterization
                           | externalDependence
                           | componentOf
                           | memberOf
                           | subCollectionOf
                           | subQualityOf
                           | instantiation
                           | termination
                           | participational
                           | participation
                           | historicalDependence
                           | creation
                           | manifestation
                           | bringsAbout
                           | triggers
                           | composition
                           | aggregation
                           | inherence
                           | value
                           | formal
                           | constitution'''
    p[0] = p[1]

def p_dado_nativo(p):
    '''dado_nativo : number
                   | string
                   | boolean
                   | date
                   | time
                   | datetime'''
    p[0] = p[1]

def p_empty(p):
    'empty :'
    p[0] = None
    pass

def p_error(p):
    if p:
        error_msg = f"Erro Sintático: Token inesperado '{p.value}' (Tipo: {p.type}) na linha {p.lineno}"
        
        suggestion = "Erro de sintaxe geral."

        if p.type == 'CLASS_ID':
             if 'datatype' in str(p.value).lower() and not str(p.value).endswith('DataType'):
                 suggestion = f"Se isso for um Datatype, o nome '{p.value}' deve terminar com 'DataType'."
             else:
                 suggestion = "Este nome apareceu em um lugar inesperado. Verifique pontuação anterior (hífens não são permitidos em nomes) ou se falta fechar chaves."

        elif p.value == '-':
             suggestion = "Hífens ('-') não são permitidos dentro de nomes de classes, atributos ou enums."
        elif p.type in ['kind', 'phase', 'role', 'category', 'mixin', 'subkind', 'relator']:
            suggestion = f"A palavra reservada '{p.value}' apareceu onde não devia. Verifique se você fechou '}}' da classe anterior."

        elif p.value == '{':
            suggestion = "Token '{' inesperado. Faltou o nome da classe ou a palavra reservada antes?"
        elif p.value == '}':
            suggestion = "Token '}' inesperado. Há chaves em excesso ou fora de lugar?"

        elif p.value in ['--', '<>--', '--<>', '<o>--', '--<o>']:
            suggestion = "Problema na definição da relação. Verifique cardinalidades [1..*] e a ordem dos elementos."

        erros_sintaticos.append(f"{error_msg}\n   -> Sugestão: {suggestion}")
        print(error_msg)
    else:
        erros_sintaticos.append("Erro Sintático: Fim inesperado do arquivo! (Verifique se fechou todos os blocos com '}')")
        print("Erro Sintático: Fim inesperado do arquivo!")

parser = yacc.yacc(debug=False)

def analisar_sintaxe(texto_codigo: str, nome_arquivo_origem: str = "exemplo_tonto"):
    erros_sintaticos.clear()
    
    lexer.lineno = 1
    resultado = parser.parse(texto_codigo, lexer=lexer)
    
    stats = {
        'pacote': "Desconhecido",
        'qtd_classes': 0,
        'qtd_relacoes_internas': 0,
        'qtd_relacoes_externas': 0,
        'qtd_datatypes': 0,
        'qtd_enums': 0,
        'qtd_gensets': 0,
        'classes_por_pacote': []
    }

    pacote = "Desconhecido"
    if resultado and resultado[2]:
        pacote = resultado[2][1]
        stats['pacote'] = pacote

    declaracoes = []
    if resultado and resultado[3]:
        declaracoes = resultado[3]

    tabela_dados = []
    
    print(f"\n--- Iniciando Análise do Pacote: {pacote} ---\n")
    
    if declaracoes:
        for decl in declaracoes:
            tipo_decl = decl[0]
            
            nome_classe = None
            estereotipo = None
            lista_atributos = []
            lista_relacoes = []
            detalhes = "-"
            corpo = None

            if tipo_decl.startswith('classe'):
                stats['qtd_classes'] += 1
                
                if tipo_decl == 'classe_com_corpo':
                    nome_classe = decl[2]
                    estereotipo = decl[1]
                    corpo = decl[3]
                elif tipo_decl == 'classe_com_corpo_e_heranca':
                    nome_classe = decl[2]
                    estereotipo = decl[1]
                    pais = ", ".join(decl[3]) if isinstance(decl[3], list) else decl[3]
                    corpo = decl[4]
                    detalhes = f"Specializes: {pais}"
                elif tipo_decl == 'classe_subtipo_complexo_com_corpo':
                    nome_classe = decl[2]
                    estereotipo = decl[1]
                    tipo_complexo = decl[3]
                    pais = ", ".join(decl[4]) if isinstance(decl[4], list) else decl[4]
                    corpo = decl[5]
                    detalhes = f"of {tipo_complexo}\nSpecializes: {pais}"
                elif tipo_decl == 'classe_subtipo_complexo':
                    nome_classe = decl[2]
                    estereotipo = decl[1]
                    tipo_complexo = decl[3] 
                    pais = ", ".join(decl[4]) if isinstance(decl[4], list) else decl[4]
                    detalhes = f"of {tipo_complexo}\nSpecializes: {pais}"
                    stats['classes_por_pacote'].append(nome_classe)
                    tabela_dados.append([nome_classe, estereotipo, "-", "-", detalhes])
                    continue
                elif tipo_decl == 'classe_complexa_com_corpo':
                    nome_classe = decl[2]
                    estereotipo = decl[1]
                    tipo_complexo = decl[3]
                    corpo = decl[4]
                    detalhes = f"of {tipo_complexo}"
                elif tipo_decl == 'classe_complexa_simples':
                    nome_classe = decl[2]
                    estereotipo = decl[1]
                    tipo_complexo = decl[3]
                    detalhes = f"of {tipo_complexo}"
                    stats['classes_por_pacote'].append(nome_classe)
                    tabela_dados.append([nome_classe, estereotipo, "-", "-", detalhes])
                    continue
                elif tipo_decl == 'classe_especializada_simples':
                    nome_classe = decl[2]
                    estereotipo = decl[1]
                    pais = ", ".join(decl[3]) if isinstance(decl[3], list) else decl[3]
                    detalhes = f"Specializes: {pais}"
                    stats['classes_por_pacote'].append(nome_classe)
                    tabela_dados.append([nome_classe, estereotipo, "-", "-", detalhes])
                    continue
                elif tipo_decl == 'classe_simples':
                    stats['classes_por_pacote'].append(decl[2])
                    tabela_dados.append([decl[2], decl[1], "-", "-", "-"])
                    continue
                
                if nome_classe:
                    stats['classes_por_pacote'].append(nome_classe)

            elif tipo_decl.startswith('datatype'):
                stats['qtd_datatypes'] += 1
                if tipo_decl == 'datatype':
                    nome_classe = decl[1]
                    estereotipo = "datatype"
                    corpo = decl[2]
                    local_atributos = []
                    if corpo:
                        for membro in corpo:
                            if membro[0] == 'atributo':
                                card = f" {membro[3]}" if membro[3] else ""
                                meta = f" {{ {membro[4]} }}" if membro[4] else ""
                                attr_str = f"{membro[1]} : {membro[2]}{card}{meta}"
                                local_atributos.append(attr_str)
                    atributos_formatados = "\n".join(local_atributos) if local_atributos else "-"
                    tabela_dados.append([nome_classe, estereotipo, atributos_formatados, "-", "-"])
                elif tipo_decl == 'datatype_specialized':
                    nome_classe = decl[1]
                    estereotipo = "datatype"
                    pais = decl[2]
                    detalhes = f"Specializes: {pais}"
                    tabela_dados.append([nome_classe, estereotipo, "-", "-", detalhes])
                continue

            elif tipo_decl == 'enum':
                stats['qtd_enums'] += 1
                nome_enum = decl[1]
                valores = decl[2]
                valores_formatados = ", ".join(valores) if isinstance(valores, list) else str(valores)
                tabela_dados.append([nome_enum, "enum", valores_formatados, "-", "-"])
                continue

            elif tipo_decl.startswith('relacao_externa'):
                stats['qtd_relacoes_externas'] += 1
                estereotipo = decl[1]
                nome_relacao = decl[2]
                card_origem = decl[3]
                card_destino = decl[5]
                alvo = decl[6]
                inverse = decl[7] 
                
                detalhes_str = "-"
                if inverse:
                    detalhes_str = f"Specializes: {inverse}"
                
                tag_display = f"relation ({estereotipo})" if estereotipo else "relation"
                
                relacao_str = ""
                if tipo_decl == 'relacao_externa':
                     relacao_str = f"{card_origem} {decl[4]} {card_destino} {alvo}"
                elif tipo_decl == 'relacao_externa_link':
                     link = decl[4]
                     link_str = f"{link[0]} {link[1]} {link[2]}"
                     relacao_str = f"({tag_display}) {card_origem} {link_str} {card_destino} {alvo}"
                elif tipo_decl == 'relacao_externa_sem_tag':
                     relacao_str = f"{card_origem} {decl[4]} {card_destino} {alvo}"
                elif tipo_decl == 'relacao_externa_sem_tag_link':
                     link = decl[4]
                     link_str = f"{link[0]} {link[1]} {link[2]}"
                     relacao_str = f"{card_origem} {link_str} {card_destino} {alvo}"

                tabela_dados.append([nome_relacao, tag_display, "-", relacao_str, detalhes_str])
                continue

            elif tipo_decl.startswith('genset'):
                stats['qtd_gensets'] += 1
                if tipo_decl == 'genset_completo' or tipo_decl == 'genset_where':
                    modifiers = decl[1]
                    name = decl[2]
                    general = decl[3] if tipo_decl == 'genset_completo' else decl[4]
                    specifics_raw = decl[4] if tipo_decl == 'genset_completo' else decl[3]
                    specifics = ", ".join(specifics_raw) if isinstance(specifics_raw, list) else str(specifics_raw)
                    
                    mods_str = ""
                    if isinstance(modifiers, tuple):
                        mods_str = " ".join(modifiers)
                    elif modifiers:
                        mods_str = str(modifiers)
                    tipo_genset = f"{mods_str} genset".strip()
                    tabela_dados.append([f"{name}", tipo_genset, "-", "-", f"General: {general} \nSpecifics: {specifics}"])
                continue

            if nome_classe:
                if corpo: 
                    for membro in corpo:
                        if membro[0] == 'atributo':
                            card = f" {membro[3]}" if membro[3] else ""
                            meta = f" {{ {membro[4]} }}" if membro[4] else ""
                            attr_str = f"{membro[1]} : {membro[2]}{card}{meta}"
                            lista_atributos.append(attr_str)
                        elif membro[0].startswith('relacao_interna'):
                            stats['qtd_relacoes_internas'] += 1
                            
                            inverse = membro[-1]
                            inverse_str = f" (Inverse: {inverse})" if inverse else ""
                            target = membro[-2]
                            constraint = membro[-3]
                            const_str = f" {constraint}" if constraint else ""
                            
                            rel_str = ""
                            if membro[0] == 'relacao_interna_padrao':
                                # @stereo [1] -- [1] Class
                                rel_str = f"({membro[1]}) {membro[2]} {membro[3]} {membro[4]} {membro[5]}"

                            elif membro[0] == 'relacao_interna_tag_link':
                                # @stereo --link-- [1] Class (SEM CARD INICIAL)
                                link = membro[2] 
                                link_str = f"{link[0]} {link[1]} {link[2]}"
                                rel_str = f"({membro[1]}) {link_str} {membro[3]} {membro[4]}"

                            elif membro[0] == 'relacao_interna_link_simples':
                                # --link-- [1] Class
                                link = membro[1]
                                link_str = f"{link[0]} {link[1]} {link[2]}"
                                rel_str = f"{link_str} {membro[2]} {membro[3]}"
                            
                            elif membro[0] == 'relacao_interna_link_duplo':
                                # [1] --link-- [1] Class
                                link = membro[2]
                                link_str = f"{link[0]} {link[1]} {link[2]}"
                                rel_str = f"{membro[1]} {link_str} {membro[3]} {membro[4]}"

                            elif membro[0] == 'relacao_interna_tag_link_duplo':
                                # @stereo [1] --link-- [1] Class
                                link = membro[3]
                                link_str = f"{link[0]} {link[1]} {link[2]}"
                                rel_str = f"({membro[1]}) {membro[2]} {link_str} {membro[4]} {membro[5]}"
                                
                            elif membro[0] == 'relacao_interna_sem_tag':
                                # [1] -- [1] Class
                                rel_str = f"{membro[1]} {membro[2]} {membro[3]} {membro[4]}"
                            
                            else: # Fallback para compatibilidade
                                rel_str = "Relacao complexa"

                            if rel_str:
                                lista_relacoes.append(rel_str)

                atributos_formatados = "\n".join(lista_atributos) if lista_atributos else "-"
                relacoes_formatadas = "\n".join(lista_relacoes) if lista_relacoes else "-"
                tabela_dados.append([nome_classe, estereotipo, atributos_formatados, relacoes_formatadas, detalhes])

    headers_det = ["Classe/Entidade", "Estereótipo", "Atributos", "Relações", "Detalhes"]
    tabela_string_det = tabulate(tabela_dados, headers=headers_det, tablefmt="grid")
    
    sintese_dados = [
        ["Pacote", stats['pacote']],
        ["Total de Classes", stats['qtd_classes']],
        ["Relações Internas", stats['qtd_relacoes_internas']],
        ["Relações Externas", stats['qtd_relacoes_externas']],
        ["Datatypes", stats['qtd_datatypes']],
        ["Enums", stats['qtd_enums']],
        ["Gensets", stats['qtd_gensets']]
    ]
    
    tabela_string_sum = tabulate(sintese_dados, tablefmt="grid")

    relatorio_erros = ""
    if erros_sintaticos:
        relatorio_erros = "\n\n=== RELATÓRIO DE ERROS ===\n"
        for i, erro in enumerate(erros_sintaticos, 1):
            relatorio_erros += f"{i}. {erro}\n"
    else:
        relatorio_erros = "\n\n=== Nenhum erro sintático encontrado. ===\n"

    print(tabela_string_det)
    print("\n=== TABELA DE SÍNTESE ===")
    print(tabela_string_sum)
    print(relatorio_erros)
    
    diretorio_atual = os.path.dirname(__file__)  
    pasta_exports = os.path.join(diretorio_atual, 'exports')
    os.makedirs(pasta_exports, exist_ok=True)
    nome_arquivo_saida = f"tabela_sintatica_{nome_arquivo_origem}.txt"
    caminho_completo = os.path.join(pasta_exports, nome_arquivo_saida)
    
    try:
        with open(caminho_completo, "w", encoding="utf-8") as f:
            f.write(f"ANÁLISE DO PACOTE: {pacote}\n\n")
            f.write("=== 1. VISUALIZAÇÃO DETALHADA ===\n")
            f.write(tabela_string_det)
            f.write("\n\n=== 2. TABELA DE SÍNTESE ===\n")
            f.write(tabela_string_sum)
            f.write(relatorio_erros)

        print(f"\n[INFO] Análise completa salva em: {caminho_completo}")

    except Exception as e:
        print(f"\n[ERRO] Não foi possível salvar o arquivo: {e}")
    
    return resultado