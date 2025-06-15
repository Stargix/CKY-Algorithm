from typing import List, Dict, Tuple, Set
from main_cky import Gramatica
from copy import deepcopy

class GramaticaFNC(Gramatica):
    def __init__(self, normes_gramatica: Dict, simbol_arrel: str = 'S') -> None:
        # Transforma la gramàtica a Forma Normal de Chomsky i inicialitza la classe base
        self.gramatica = deepcopy(normes_gramatica)
        self._forma_normal_chomsky()
        super().__init__(self.gramatica, simbol_arrel)
        
    def _forma_normal_chomsky(self) -> None:
        """
        Transforma la gramàtica a Forma Normal de Chomsky (FNC).
        :return: Retorna True si la transformació s'ha completat correctament.
        """
        self._eliminar_produccions_buides() # (A -> ε)
        self._eliminar_regles_unitaries() # (A -> B)
        self._convertir_regles_terminals() # A -> a
        self._convertir_regles_llargues() # (A -> BC...Z)
    
    def _generar_combinacions(self, produccio: List[str], buides: Set[str]) -> Set[Tuple[str]]:
        """
        Genera totes les combinacions possibles de produccions eliminant els no-terminals que són buits.
        :param produccio: Producció original.
        :param buides: Conjunt de no-terminals que poden derivar a la cadena buida.
        :return: Un conjunt de tuples amb les noves produccions.
        """
        if not produccio:
            return {tuple()}

        resultats = set()
        # Always include the original production
        resultats.add(tuple(produccio))
        
        # Generate combinations by removing nullable symbols
        for i in range(len(produccio)):
            if produccio[i] in buides:
                # Generate combinations without this symbol
                sub_combinations = self._generar_combinacions(produccio[:i] + produccio[i+1:], buides)
                resultats.update(sub_combinations)

        return resultats

    def _eliminar_produccions_buides(self):
        buides = {nt for nt, prod in self.gramatica.items() if [["ε"]] in prod or [[""]] in prod or ["ε"] in prod or [""] in prod}
        while True:
            nous_buits = buides.copy()
            for nt, prod in self.gramatica.items():
                for p in prod:
                    if p and all(s in buides for s in p):
                        nous_buits.add(nt)
            if nous_buits == buides:
                break
            buides = nous_buits

        for nt in self.gramatica:
            noves_prod = set()
            for p in self.gramatica[nt]:
                if p == ["ε"] or p == [""]:
                    continue
                noves_prod.update(self._generar_combinacions(p, buides))
            self.gramatica[nt] = [list(p) for p in noves_prod if p and p != ("ε",) and p != ("",)]

    def _eliminar_regles_unitaries(self):
        canviat = True
        while canviat:
            canviat = False
            for no_terminal, produccions in self.gramatica.items():
                noves_prod = []
                for produccio in produccions:
                    if len(produccio) == 1 and produccio[0] in self.gramatica:
                        # És una regla unitària
                        for sub_produccio in self.gramatica[produccio[0]]:
                            if sub_produccio not in noves_prod:
                                noves_prod.append(sub_produccio)
                                canviat = True
                    else:
                        noves_prod.append(produccio)
                self.gramatica[no_terminal] = noves_prod

    def _convertir_regles_terminals(self):
        """
        Converteix regles com (A -> ab) en regles no terminals separades (A -> T1 T2) 
        on Tn és un nou no-terminal (T1 -> a) (T2 -> b)

        Pressuposa que les regles terminals estàn escrites en minúscules
        És important que 
        """

        contador = 1
        conjunt_terminals = {}

        for no_terminal, produccions in self.gramatica.items():
                noves_produccions = []

                for produccio in produccions:
                    nova_prod = []
        
                    for simbol in produccio:
                        if simbol.islower() and len(produccio) > 1: # És una terminal en una regla llarga
                            if simbol not in conjunt_terminals:
                                nou_no_terminal = f"T{contador}"
                                contador += 1
                                conjunt_terminals[simbol] = nou_no_terminal
                                self.gramatica[nou_no_terminal] = [[simbol]]

                            nova_prod.append(conjunt_terminals[simbol])

                        else:
                            nova_prod.append(simbol)

                    noves_produccions.append(nova_prod)

                self.gramatica[no_terminal] = noves_produccions

    def _convertir_regles_llargues(self):
        contador = 1
        for nt in list(self.gramatica.keys()):
            noves_prod = []
            for p in self.gramatica[nt]:
                while len(p) > 2:
                    nou_nt = f"X{contador}"
                    contador += 1
                    self.gramatica[nou_nt] = [[p[0], p[1]]]
                    p = [nou_nt] + p[2:]
                noves_prod.append(p)
            self.gramatica[nt] = noves_prod

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

examen_plh = {
    'S': [['NP', 'VP']],
    'NP': [['DT', 'NN'], ['DT', 'NNS'], ['groucho'], ['shot'], ['elephant'], ['NP', 'PP']],
    'PP': [['IN', 'NP']],
    'VP': [['VP', 'PP'], ['VP', 'NP'], ['shot']],
    'NN': [['shot'], ['elephant']],
    'NNS': [['pajamas']],
    'DT': [['an'], ['his']],
    'IN': [['in']]
}

plh_probabilitat = {
    'S': [ (['NP', 'VP'], 1.0) ],
    'NP': [
        (['DT', 'NN'], 0.4),
        (['DT', 'NNS'], 0.3),
        (['Groucho'], 0.01),
        (['shot'], 0.03),
        (['elephant'], 0.04),
        (['NP', 'PP'], 0.2)
    ],
    'PP': [ (['IN', 'NP'], 1.0) ],
    'VP': [
        (['VP', 'PP'], 0.5),
        (['VP', 'NP'], 0.4),
        (['shot'], 0.03)
    ],
    'NN': [
        (['shot'], 0.02),
        (['elephant'], 0.03)
    ],
    'NNS': [ (['pajamas'], 0.02) ],
    'DT': [
        (['an'], 0.2),
        (['his'], 0.1)
    ],
    'IN': [ (['in'], 0.1) ]
}

k = GramaticaFNC(examen_plh)
print("\nGramatica FNC del examen:")
print(k)

res = k.algoritme_cky("groucho shot an elephant in his pajamas".split())
print("\nResultat de l'algoritme CKY per l'examen:", res)
