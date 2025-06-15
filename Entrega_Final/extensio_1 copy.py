from typing import List, Dict, Tuple, Set
from main_cky import Gramatica
from copy import deepcopy

def forma_normal_chomsky(gramatica: dict) -> dict:
    """
    Transforma una gramàtica a Forma Normal de Chomsky (FNC).
    :param gramatica: Diccionari amb la gramàtica original
    :return: Diccionari amb la gramàtica transformada a FNC
    """
    # Creem una copia per evitar aliasing
    gramatica_fnc = deepcopy(gramatica)
    eliminar_produccions_buides(gramatica_fnc) # (A -> ε) 
    eliminar_regles_unitaries(gramatica_fnc) # (A -> B)
    convertir_regles_terminals(gramatica_fnc) # (A -> a)
    convertir_regles_llargues(gramatica_fnc) # (A -> BC...Z -> BC)
    
    return gramatica_fnc

def generar_combinacions(produccio: List[str], buides: Set[str]) -> Set[Tuple[str]]:
    """
    Genera totes les combinacions possibles de produccions eliminant els no-terminals que són buits.
    """
    if not produccio:
        return {tuple()}

    resultats = set()
    resultats.add(tuple(produccio))
    
    for i in range(len(produccio)):
        if produccio[i] in buides:
            sub_combinations = generar_combinacions(produccio[:i] + produccio[i+1:], buides)
            resultats.update(sub_combinations)

    return resultats

def eliminar_produccions_buides(gramatica: dict):
    """Elimina produccions buides de la gramàtica"""
    buides = {nt for nt, prod in gramatica.items() 
             if [["ε"]] in prod or [[""]] in prod or ["ε"] in prod or [""] in prod}
    
    while True:
        nous_buits = buides.copy()
        for nt, prod in gramatica.items():
            for p in prod:
                if p and all(s in buides for s in p):
                    nous_buits.add(nt)
        if nous_buits == buides:
            break
        buides = nous_buits

    for nt in gramatica:
        noves_prod = set()
        for p in gramatica[nt]:
            if p == ["ε"] or p == [""]:
                continue
            noves_prod.update(generar_combinacions(p, buides))
        gramatica[nt] = [list(p) for p in noves_prod if p and p != ("ε",) and p != ("",)]

def eliminar_regles_unitaries(gramatica: dict):
    """Elimina regles unitàries de la gramàtica"""
    canviat = True
    while canviat:
        canviat = False
        for no_terminal, produccions in gramatica.items():
            noves_prod = []
            for produccio in produccions:
                if len(produccio) == 1 and produccio[0] in gramatica:
                    # És una regla unitària
                    for sub_produccio in gramatica[produccio[0]]:
                        if sub_produccio not in noves_prod:
                            noves_prod.append(sub_produccio)
                            canviat = True
                else:
                    noves_prod.append(produccio)
            gramatica[no_terminal] = noves_prod

def convertir_regles_llargues(gramatica: dict):
    """Converteix regles llargues a regles binàries"""
    contador = 1
    for nt in list(gramatica.keys()):
        noves_prod = []
        for p in gramatica[nt]:
            while len(p) > 2:
                nou_nt = f"X{contador}"
                contador += 1
                gramatica[nou_nt] = [[p[0], p[1]]]
                p = [nou_nt] + p[2:]
            noves_prod.append(p)
        gramatica[nt] = noves_prod

def convertir_regles_terminals(gramatica: dict):
    """Converteix regles terminals per assegurar la forma A -> a"""
    contador = 1
    terminals_map = {}
    for nt in list(gramatica.keys()):
        noves_prod = []
        for p in gramatica[nt]:
            nova_p = []
            for s in p:
                if s.islower() and len(p) > 1:  # És un terminal en una regla llarga
                    if s not in terminals_map:
                        nou_nt = f"T{contador}"
                        contador += 1
                        terminals_map[s] = nou_nt
                        gramatica[nou_nt] = [[s]]
                    nova_p.append(terminals_map[s])
                else:
                    nova_p.append(s)
            noves_prod.append(nova_p)
        gramatica[nt] = noves_prod

class GramaticaFNC(Gramatica):
    def __init__(self, normes_gramatica: Dict, simbol_arrel: str = 'S') -> None:
        # Transforma la gramàtica a Forma Normal de Chomsky i inicialitza la classe base
        gramatica_fnc = forma_normal_chomsky(normes_gramatica)
        super().__init__(gramatica_fnc, simbol_arrel)


xd = {
        'S': [['NP', 'VP']],
        'NP': [['Det', 'N'], ['Det', 'Adj', 'N']],
        'VP': [['V', 'NP']],
        'Det': [['els']],
        'N': [['carbassots'], ['pardimolls']],
        'Adj': [['millors']],
        'V': [['són']]
    }

x = Gramatica(xd)
g = GramaticaFNC(xd)
print("\nGramatica original:")
print(x)
print("\nGramatica FNC:")
print(g)


res = g.algoritme_cky("els carbassots són els millors pardimolls".split())
print("\nResultat de l'algoritme CKY:", res)
