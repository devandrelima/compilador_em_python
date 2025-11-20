import ply.yacc as yacc
from lexico_analyzer.lexer_puro import tokens, lexer
from tabulate import tabulate

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
                         | estereotipo_subtipo CLASS_ID specializes lista_ids
                         | estereotipo_subtipo CLASS_ID of estereotipo_complexo specializes lista_ids
                         | estereotipo_classe CLASS_ID""" 
    
    if len(p) == 6:
        p[0] = ('classe_com_corpo', p[1], p[2], p[4])
    
    elif len(p) > 3:
        if len(p) == 7:
            # p[0] = (tag, estereotipo, nome, TIPO_COMPLEXO, pais)
            p[0] = ('classe_subtipo_complexo', p[1], p[2], p[4], p[6])
        
        elif len(p) == 5:
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
                            | intrinsic_modes'''
    p[0] = p[1]

def p_lista_ids(p):
    """lista_ids : CLASS_ID ',' lista_ids
                 | CLASS_ID"""
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

def p_declaracao_atributo(p):
    "declaracao_atributo : RELATION_ID ':' tipo meta_atributos_opt"
    p[0] = ('atributo', p[1], p[3], p[4])

def p_tipo(p):
    '''tipo : dado_nativo
            | NEW_TYPE
            | CLASS_ID'''
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
    "declaracao_tipo_dado : datatype CLASS_ID '{' corpo_classe '}'"
    p[0] = ('datatype', p[2], p[4]) 

def p_declaracao_enum(p):
    "declaracao_enum : enum CLASS_ID '{' lista_instancias_enum '}'"
    p[0] = ('enum', p[2], p[4]) 

def p_lista_instancias_enum(p):
    """lista_instancias_enum : CLASS_ID ',' lista_instancias_enum
                             | CLASS_ID"""
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

def p_declaracao_genset(p):
    """declaracao_genset : genset_modifiers_opt genset CLASS_ID where lista_classes_genset specializes CLASS_ID
                         | genset_modifiers_opt genset CLASS_ID '{' genset_corpo '}'
                         | genset_modifiers_opt genset '{' genset_corpo '}'
                         | genset genset_modifiers_opt CLASS_ID '{' genset_corpo '}'
                         | genset genset_modifiers_opt '{' genset_corpo '}'"""
    
    modifiers = None
    name = "Anônimo"
    general = None
    specifics = []

    if len(p) == 8:
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

def p_declaracao_relacao_interna(p):
    '''declaracao_relacao_interna : '@' estereotipo_relacao CARDINALITY simbolo_associacao CARDINALITY CLASS_ID
                                  | '@' estereotipo_relacao link_nomeado CARDINALITY CLASS_ID
                                  | link_nomeado CARDINALITY CLASS_ID'''
    if len(p) == 7:
        p[0] = ('relacao_interna', p[2], p[3], p[4], p[5], p[6])
    elif len(p) == 6:
        p[0] = ('relacao_interna_nomeada', p[2], p[3], p[4], p[5])
    else:
        p[0] = ('relacao_interna_sem_tag', None, p[1], p[2], p[3])

def p_link_nomeado(p):
    '''link_nomeado : ASSOCIATION RELATION_ID ASSOCIATION
                    | COMPOSITION_L RELATION_ID ASSOCIATION
                    | COMPOSITION_R RELATION_ID ASSOCIATION
                    | COMPOSITION_LO RELATION_ID ASSOCIATION
                    | COMPOSITION_RO RELATION_ID ASSOCIATION'''
    p[0] = p[2] 

def p_declaracao_relacao_externa(p):
    "declaracao_relacao_externa : '@' estereotipo_relacao relation CLASS_ID CARDINALITY simbolo_associacao CARDINALITY CLASS_ID"
    p[0] = ('relacao_externa', p[2], p[4], p[5], p[6], p[7], p[8])

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
                          | relator'''
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
        print(f"Erro de Sintaxe: Token inesperado '{p.value}' (Tipo: {p.type}) na linha {p.lineno}")
    else:
        print("Erro de Sintaxe: Fim inesperado do arquivo! (Verifique se fechou todos os '{' '}')")

parser = yacc.yacc(debug=False)

def analisar_sintaxe(texto_codigo: str):
    lexer.lineno = 1
    resultado = parser.parse(texto_codigo, lexer=lexer)
    
    if not resultado:
        print("Nenhum resultado gerado.")
        return

    pacote = resultado[2][1] if resultado[2] else "Desconhecido"
    declaracoes = resultado[3]
    
    tabela_dados = []
    
    print(f"\nPacote Detectado: {pacote}\n")
    
    if declaracoes:
        for decl in declaracoes:
            tipo_decl = decl[0]
            
            if tipo_decl == 'classe_com_corpo':
                nome_classe = decl[2]
                estereotipo = decl[1]
                corpo = decl[3]
                
                lista_atributos = []
                lista_relacoes = []
                
                if corpo:
                    for membro in corpo:
                        if membro[0] == 'atributo':
                            attr_str = f"{membro[1]} : {membro[2]}"
                            lista_atributos.append(attr_str)
                        elif membro[0].startswith('relacao_interna'):
                            if membro[0] == 'relacao_interna':
                                rel_str = f"{membro[5]} ({membro[1]})"
                                lista_relacoes.append(rel_str)
                            elif membro[0] == 'relacao_interna_nomeada':
                                rel_str = f"{membro[4]} ({membro[1]} - {membro[2]})"
                                lista_relacoes.append(rel_str)
                            elif membro[0] == 'relacao_interna_sem_tag':
                                rel_str = f"{membro[4]} ({membro[2]})"
                                lista_relacoes.append(rel_str)

                atributos_formatados = "\n".join(lista_atributos) if lista_atributos else "-"
                relacoes_formatadas = "\n".join(lista_relacoes) if lista_relacoes else "-"
                
                tabela_dados.append([nome_classe, estereotipo, atributos_formatados, relacoes_formatadas, "-"])

            elif tipo_decl == 'datatype':
                nome_classe = decl[1]
                estereotipo = "datatype"
                corpo = decl[2]
                
                lista_atributos = []
                
                if corpo:
                    for membro in corpo:
                        if membro[0] == 'atributo':
                            attr_str = f"{membro[1]} : {membro[2]}"
                            lista_atributos.append(attr_str)
                
                atributos_formatados = "\n".join(lista_atributos) if lista_atributos else "-"
                tabela_dados.append([nome_classe, estereotipo, atributos_formatados, "-", "-"])

            elif tipo_decl == 'enum':
                nome_enum = decl[1]
                valores = decl[2]
                valores_formatados = ", ".join(valores) if isinstance(valores, list) else str(valores)
                tabela_dados.append([nome_enum, "enum", valores_formatados, "-", "-"])

            elif tipo_decl == 'classe_especializada_simples':
                pais = ", ".join(decl[3]) if isinstance(decl[3], list) else decl[3]
                tabela_dados.append([decl[2], decl[1], "-", "-", f"Specializes: {pais}"])
                
            elif tipo_decl == 'classe_subtipo_complexo':
                tipo_complexo = decl[3]
                pais = ", ".join(decl[4]) if isinstance(decl[4], list) else decl[4]
                
                detalhes = f"of {tipo_complexo}\nSpecializes: {pais}"
                
                tabela_dados.append([decl[2], decl[1], "-", "-", detalhes])
                
            elif tipo_decl == 'classe_simples':
                tabela_dados.append([decl[2], decl[1], "-", "-", "-"])

            elif tipo_decl == 'relacao_externa':
                estereotipo = decl[1]
                nome_relacao = decl[2]
                alvo = decl[6]
                
                relacao_str = f"{alvo}"
                
                tabela_dados.append([nome_relacao, f"Relation ({estereotipo})", "-", relacao_str, "-"])

            elif tipo_decl == 'genset_completo':
                modifiers = decl[1]
                name = decl[2]
                general = decl[3]
                specifics = ", ".join(decl[4]) if isinstance(decl[4], list) else str(decl[4])
                
                mods_str = ""
                if isinstance(modifiers, tuple):
                    mods_str = " ".join(modifiers)
                elif modifiers:
                    mods_str = str(modifiers)
                
                tipo_genset = f"{mods_str} genset".strip()
                
                tabela_dados.append([f"{name}", tipo_genset, "-", "-", f"General: {general} \nSpecifics: {specifics}"])

            elif tipo_decl == 'genset_where':
                modifiers = decl[1]
                name = decl[2]
                specifics = ", ".join(decl[3]) if isinstance(decl[3], list) else str(decl[3])
                general = decl[4]

                mods_str = ""
                if isinstance(modifiers, tuple):
                    mods_str = " ".join(modifiers)
                elif modifiers:
                    mods_str = str(modifiers)
                
                tipo_genset = f"{mods_str} genset".strip()
                tabela_dados.append([f"{name}", tipo_genset, "-", "-", f"General: {general} \nSpecifics: {specifics}"])

    headers = ["Classe", "Estereótipo", "Atributos Internos", "Relações", "Detalhes (Herança ou Generalização)"]
    
    print(tabulate(tabela_dados, headers=headers, tablefmt="grid"))
    
    print("\nPrograma Tonto Reconhecido!")
    return resultado