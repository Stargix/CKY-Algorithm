from typing import List, Set, Tuple
from cky import Gramatica
from copy import deepcopy

class GramaticaFNC(Gramatica):
    def __init__(self, normes_gramatica: set, simbol_arrel: str = 'S') -> None:
        copia_normes_gramatica = deepcopy(normes_gramatica) # Evita aliasing
        super().__init__(copia_normes_gramatica, simbol_arrel)
        self.normes_gramatica = copia_normes_gramatica
        self._forma_normal_chomsky() # Transformem la gramàtica a FNC
        self.regles_binaries = self._preprocessar_regles_binaries()
        self.simbol_arrel = simbol_arrel

    def _forma_normal_chomsky(self) -> None:
        """
        Transforma la gramàtica a Forma Normal de Chomsky (FNC).
        :return: Retorna True si la transformació s'ha completat correctament.
        """
        # 1. Eliminar produccions buides (A -> ε)
        self._eliminar_produccions_buides()
        # 2. Eliminar regles unitàries (A -> B)
        self._eliminar_regles_unitaries()
        # 3. Convertir regles llargues a regles binàries (A -> BC...Z)
        self._convertir_regles_llargues()
        # 4. Assegurar que les regles terminals siguin A -> a
        self._convertir_regles_terminals()
    
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

    def _convertir_regles_terminals(self):
        """
        Converteix regles com (A -> aBc) en regles separades (A -> Tn) on Tn és un nou no-terminal.

        Pressuposa que les regles terminals estàn escrites en minúscules
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
                                nou_no_terminal = f"T{contador}" # Afegim un nou no-terminal per la regla
                                contador += 1
                                conjunt_terminals[simbol] = nou_no_terminal
                                self.gramatica[nou_no_terminal] = [[simbol]]

                            nova_prod.append(conjunt_terminals[simbol])

                        else:
                            nova_prod.append(simbol) # Si no és una terminal, l'afegim tal qual

                    noves_produccions.append(nova_prod)

                self.gramatica[no_terminal] = noves_produccions


if __name__ == "__main__":

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
