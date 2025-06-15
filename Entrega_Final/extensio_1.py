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
        resultats.add(tuple(produccio)) # Sempre inclou la producció original
 
        for i in range(len(produccio)):
            if produccio[i] in buides:
                sub_combinations = self._generar_combinacions(produccio[:i] + produccio[i+1:], buides)
                resultats.update(sub_combinations)

        return resultats

    def _eliminar_produccions_buides(self):
        """
        Elimina produccions buides de la gramàtica (A -> ε)
        Aquesta funció identifica els no-terminals que poden derivar a la cadena buida i elimina les produccions que només contenen aquests no-terminals. 
        Per exemple, si tenim A -> ε i B -> A C, llavors B es converteix en B -> C.
        """
        buides = {no_terminal for no_terminal, produccions in self.gramatica.items() 
                  if [["ε"]] in produccions or [[""]] in produccions or ["ε"] in produccions or [""] in produccions}
        canvi = True
        while canvi:
            canvi = False
            nous_buides = buides.copy()

            for no_terminal, produccions in self.gramatica.items():
                for produccio in produccions:
                    if produccio and all(simbol in buides for simbol in produccio):

                        if no_terminal not in nous_buides:
                            nous_buides.add(no_terminal)
                            canvi = True

            buides = nous_buides

        for no_terminal in self.gramatica:
            noves_produccions = set()

            for produccio in self.gramatica[no_terminal]:
                if not (produccio == ["ε"] or produccio == [""]):
                    noves_produccions.update(self._generar_combinacions(produccio, buides))

            self.gramatica[no_terminal] = [list(prod) for prod in noves_produccions if prod and prod != ("ε") and prod != ("")]

    def _eliminar_regles_unitaries(self):
        """
        Elimina regles unitàries de la gramàtica (A -> B)
        Aquesta funció transforma regles unitàries en regles que contenen les produccions de B.
        Per exemple, si tenim A -> B i B -> C D, llavors A es converteix en A -> C D.
        """
        canviat = True
        while canviat:
            canviat = False
            for no_terminal, produccions in self.gramatica.items():
                noves_produccions = []
                for produccio in produccions:
                    if len(produccio) == 1 and produccio[0] in self.gramatica:
                        # És una regla unitària
                        for sub_produccio in self.gramatica[produccio[0]]:
                            if sub_produccio not in noves_produccions:
                                noves_produccions.append(sub_produccio)
                                canviat = True
                    else:
                        noves_produccions.append(produccio)
                self.gramatica[no_terminal] = noves_produccions

    def _convertir_regles_terminals(self):
        """
        Converteix regles com (A -> ab) en regles no terminals separades (A -> T1 T2) 
        on Tn és un nou no-terminal (T1 -> a) (T2 -> b)

        Pressuposa que les regles terminals estàn escrites en minúscules
        És important que 
        """
        contador = 1
        conjunt_terminals = {}

        for no_terminal, produccions in list(self.gramatica.items()):
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
        """
        Converteix regles llargues a regles binàries, és a dir, transforma regles amb més de dos símbols en regles que només tenen dues parts.
        Per exemple, A -> B C D es converteix en A -> X1 D i X1 -> B C, on X1 és un nou no-terminal.
        """
        contador = 1
        for no_terminal, produccions in list(self.gramatica.items()):
            noves_produccions = []

            for produccio in produccions:
                while len(produccio) > 2:
                    nou_no_terminal = f"X{contador}"
                    contador += 1
                    self.gramatica[nou_no_terminal] = [[produccio[0], produccio[1]]]
                    produccio = [nou_no_terminal] + produccio[2:]

                noves_produccions.append(produccio)
            self.gramatica[no_terminal] = noves_produccions