import ply.yacc as yacc
from lexico_analyzer.lexer_puro import tokens, lexer

def p_programa(p):
    'programa : lista_imports_opt declaracao_pacote lista_declaracoes_opt'
    p[0] = ('programa', p[1], p[2], p[3])
    print("Programa reconhecido com sucesso.")

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
    print(f"import de '{p[2]}'")

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
    print(f"Declaração de pacote '{p[2]}'")

def p_declaracao_classe(p):
    """declaracao_classe : estereotipo_classe CLASS_ID '{' corpo_classe '}'
                         | estereotipo_classe CLASS_ID specializes lista_ids
                         | estereotipo_subtipo CLASS_ID specializes lista_ids
                         | estereotipo_subtipo CLASS_ID of estereotipo_complexo specializes lista_ids
                         | estereotipo_classe CLASS_ID""" 
    
    if len(p) == 6:
        p[0] = ('classe_com_corpo', p[1], p[2], p[4])
        print(f"classe/relator '{p[2]}' (Tipo: {p[1]}) com corpo.")
    
    elif len(p) > 3:
        
        if len(p) == 7:
            p[0] = ('classe_subtipo_complexo', p[1], p[2], p[4], p[6])
            print(f"classe '{p[2]}' (Tipo: {p[1]}) do tipo {p[4]} especializando {p[6]}")
        
        elif len(p) == 5:
            p[0] = ('classe_especializada_simples', p[1], p[2], p[4]) 
            print(f"classe '{p[2]}' (Tipo: {p[1]}) especializando {p[4]}")
        
    else:
        p[0] = ('classe_simples', p[1], p[2])
        print(f"classe '{p[2]}' (Tipo: {p[1]})")

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
    print(f"atributo '{p[1]}'")

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
    print(f"datatype '{p[2]}'")

def p_declaracao_enum(p):
    "declaracao_enum : enum CLASS_ID '{' lista_instancias_enum '}'"
    p[0] = ('enum', p[2], p[4]) 
    print(f"enum '{p[2]}'")

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
    
    if len(p) == 8:
        p[0] = ('genset_where', p[1], p[3], p[5], p[7])
    
    elif len(p) == 6:
        if p[2] == 'genset':
            p[0] = ('genset_corpo_nomeado', p[1], p[3], p[5])
        else:
            p[0] = ('genset_corpo_nomeado', p[2], p[3], p[5])

    elif len(p) == 5:
        if p[2] == 'genset':
            p[0] = ('genset_corpo_sem_nome', p[1], p[4])
        else:
            p[0] = ('genset_corpo_sem_nome', p[2], p[4])

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
    print(f"Genset")
    print(f"Relação interna '{p[2]}' especificando '{p[4]}'")

def p_declaracao_relacao_interna(p):
    '''declaracao_relacao_interna : '@' estereotipo_relacao CARDINALITY simbolo_associacao CARDINALITY CLASS_ID
                                  | '@' estereotipo_relacao link_nomeado CARDINALITY CLASS_ID
                                  | link_nomeado CARDINALITY CLASS_ID'''
    
    if len(p) == 7:
        p[0] = ('relacao_interna', p[2], p[3], p[4], p[5], p[6])
        print(f"Relação interna padrão '{p[2]}'")

    elif len(p) == 6:
        p[0] = ('relacao_interna_nomeada', p[2], p[3], p[4], p[5])
        print(f"Relação '{p[3]}' (Estereótipo: {p[2]})")
        
    else:
        p[0] = ('relacao_interna_sem_tag', None, p[1], p[2], p[3])
        print(f"Relação '{p[1]}' (Sem estereótipo)")

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
    print(f"relação externa (Estereótipo: {p[2]})")

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

parser = yacc.yacc(debug=True) 

def analisar_sintaxe(texto_codigo: str):
    lexer.lineno = 1
    return parser.parse(texto_codigo, lexer=lexer)