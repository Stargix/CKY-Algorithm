import typing
from typing import Dict, List, Set, Tuple, Union

class Gramatica():
    def __init__(self, normes_gramatica: Set, simbol_arrel: str = 'S') -> None:
        # Convert string productions to list format for consistency
        self.gramatica = normes_gramatica
        self.regles_binaries = self._preprocessar_gramatica()
        self.simbol_arrel = simbol_arrel
        
    def algoritme_cky(self, frase: Union[List[str], str]) -> bool:
        """
        Analitza una frase gramaticalment utilitzant l'algoritme CKY.
        Omple la taula dinàmica de CKY amb la frase donada.
        :param frase: Es tracta de la cadena que volem analitzar (str o List[str]).
        :return: Retorna un boolean que inidica si la cadena es pot derivar o no.
        """

        if " " in frase:
            frase = frase.split()
        
        if not frase:
            # Comprovem si la cadena buida és derivable (S -> ε)
            return self._comprovar_derivacio_buida()
        
        n = len(frase)
        # Crear tabla como diccionario - CORREGIDO
        taula = [[set() for _ in range(n)] for _ in range(n)]

        # Omplim la primera fila (cas base): terminals
        for col in range(n):
            paraula = frase[col]
            for no_terminal, produccions in self.gramatica.items():
                for produccio in produccions:
                    # Comprovem les produccions terminals (A -> a)
                    if len(produccio) == 1 and produccio[0] == paraula:
                        taula[col][col].add(no_terminal)
                        
        
        # Omplim la resta de la taula (longitud 2 a n)
        for n_fila in range(1, n):  # longitud de la subcadena
            for diag in range(n - n_fila):
                col = diag + n_fila
                # Provem totes les possibles divisions de la subcadena
                for k in range(n_fila):
                    part_diag = taula[diag][diag + k]
                    part_col = taula[diag + k + 1][col]
                    # Si alguna de les dues parts és buida, no podem continuar
                    if not part_diag or not part_col:
                        continue
                    
                    # Comprovem totes les regles de la gramàtica per produccions binàries
                    for no_terminal_diag in part_diag:
                        for no_termina_col in part_col:
                            # Comprovem les produccions binàries (A -> BC)
                            clau = (no_terminal_diag, no_termina_col)
                            if clau in self.regles_binaries:
                                taula[diag][col].update(self.regles_binaries[clau])
  
        return self.simbol_arrel in taula[0][n-1]

                
    def _preprocessar_gramatica(self) -> Dict[Tuple[str, str], Set[str]]:
        """ 
        Preprocessa la gramàtica per accés ràpid a les regles binàries.
        Aquesta funció crea un diccionari on les claus són tuples (esq, dre) i els valors són conjunts de no-terminals.
        """
        regles_binaries = {}  # Diccionari on (esq, dre) -> {no_terminal}
        
        for no_terminal, produccions in self.gramatica.items():
            for produccio in produccions:
                if len(produccio) == 2:  # Només regles binaries
                    clau = (produccio[0], produccio[1])
                    if clau not in regles_binaries:
                        regles_binaries[clau] = set()
                    regles_binaries[clau].add(no_terminal)

        return regles_binaries
    
    def _comprovar_derivacio_buida(self) -> bool:
        """ 
        Comprova si la cadena buida és derivable a partir del símbol d'inici. 
        """
        if self.simbol_arrel in self.gramatica:
            for produccio in self.gramatica[self.simbol_arrel]:
                if len(produccio) == 1 and produccio[0] in ['ε', '']:
                    return True
        return False
    
    def forma_normal_chomsky(self) -> bool:
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
        
        # 5. Update binary rules after transformation
        self.regles_binaries = self._preprocessar_gramatica()

        return True
    
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
        changed = True
        while changed:
            changed = False
            for nt in list(self.gramatica.keys()):
                noves_prod = []
                for p in self.gramatica[nt]:
                    if len(p) == 1 and p[0] in self.gramatica:
                        # És una regla unitària
                        for sub_p in self.gramatica[p[0]]:
                            if sub_p not in noves_prod:
                                noves_prod.append(sub_p)
                                changed = True
                    else:
                        noves_prod.append(p)
                self.gramatica[nt] = noves_prod

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
        contador = 1
        terminals_map = {}
        for nt in list(self.gramatica.keys()):
            noves_prod = []
            for p in self.gramatica[nt]:
                nova_p = []
                for s in p:
                    if s.islower() and len(p) > 1:  # És un terminal en una regla llarga
                        if s not in terminals_map:
                            nou_nt = f"T{contador}"
                            contador += 1
                            terminals_map[s] = nou_nt
                            self.gramatica[nou_nt] = [[s]]
                        nova_p.append(terminals_map[s])
                    else:
                        nova_p.append(s)
                noves_prod.append(nova_p)
            self.gramatica[nt] = noves_prod
        
        

    def __str__(self):
        """
        Retorna una representació en forma de cadena de la gramàtica.
        """
        return "\n".join(
            f"{no_terminal} -> {', '.join(' '.join(map(str, produccio)) for produccio in produccions)}"
            for no_terminal, produccions in self.gramatica.items()
        )
    

    

def create_grammar_g1():
    """
    Create the first example grammar G1:
    S → a | XA | AX | b
    A → RB
    B → AX | b | a
    X → a
    R → XB
    """
    return {
        'S': [['a'], ['X', 'A'], ['A', 'X'], ['b']],
        'A': [['R', 'B']],
        'B': [['A', 'X'], ['b'], ['a']],
        'X': [['a']],
        'R': [['X', 'B']]
    }

def create_grammar_g2():
    """
    Create the second example grammar G2:
    S → AB | CD | CB | SS
    A → BC | a
    B → SC | b
    C → DD | b
    D → BA
    """
    return {
        'S': [['A', 'B'], ['C', 'D'], ['C', 'B'], ['S', 'S']],
        'A': [['B', 'C'], ['a']],
        'B': [['S', 'C'], ['b']],
        'C': [['D', 'D'], ['b']],
        'D': [['B', 'A']]
    }

def create_grammar_no_normalitzada():
    """
    Create a non-normalized grammar:
    S → AB | CD | CB | SS
    A → BC | a
    B → C | b
    C → DD | b
    D → BAC
    """
    return {
        'S': [['A', 'B'], ['C', 'D'], ['C', 'B'], ['S', 'S']],
        'A': [['B', 'C'], ['a']],
        'B': [['C'], ['b']],
        'C': [['D', 'D'], ['b']],
        'D': [['B', 'A', 'C']]
    }

def create_grammar_oracio():
    """
    Create a grammar for the sentence "els carbassots són els millors pardimolls":
    S → NP VP
    NP → Det N | Det Adj N
    VP → V NP
    Det → 'els'
    N → 'carbassots' | 'pardimolls'
    Adj → 'millors'
    V → 'són'
    """
    return {
        'S': [['NP', 'VP']],
        'NP': [['Det', 'N'], ['Det', 'Adj', 'N']],
        'VP': [['V', 'NP']],
        'Det': [['els']],
        'N': [['carbassots'], ['pardimolls']],
        'Adj': [['millors']],
        'V': [['són']]
    }



def main():
    gramatica_4 = Gramatica(create_grammar_oracio(), simbol_arrel='S')
    print("Grammar before CNF:")
    print(gramatica_4)
    print()
    
    gramatica_4.forma_normal_chomsky()
    print("Grammar after CNF:")
    print(gramatica_4)
    print()
    
    print("Binary rules:")
    print(gramatica_4.regles_binaries)
    print()
    
    result = gramatica_4.algoritme_cky("els carbassots són els millors pardimolls")
    print(f"Result: {result}")

    gramatica_2 = Gramatica(create_grammar_g2(), simbol_arrel='S')
    print("\nProva amb la gramàtica G2")
    print(gramatica_2)
    gramatica_2.forma_normal_chomsky()
    frases_g2 = ["ab", "bb", "a", "b", "abb", "bab", "abab", "bbbb", "aabb"]
    for frase in frases_g2:
        print(f"Frase: '{frase}'", end=" -> ")
        print(gramatica_2.algoritme_cky(frase))

if __name__ == "__main__":
    main()