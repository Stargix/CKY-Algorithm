from typing import Dict, List, Set, Tuple, Union
#from extensio_1 import forma_normal_chomsky

class GramaticaProbabilistica():
    def __init__(self, normes_gramatica: Dict, simbol_arrel: str = 'S') -> None:

        self.gramatica = normes_gramatica
        self.regles_binaries = self._preprocessar_gramatica()
        self.simbol_arrel = simbol_arrel
        self.arbre_gramatical = None

    def carregar_gramatica(self) -> None:
        """
        Carreguem una gramàtica en forma normal de Chomsky (CNF).
        :param normes_gramatica: Diccionari on les claus són no-terminals i els valors són llistes de produccions.
        :param simbol_arrel: El símbol d'inici de la gramàtica (per defecte li posarem 'S').
        """
        
        
    def algoritme_pcky(self, frase: Union[List[str], str]) -> bool:
        """
        Analitza una frase gramaticalment utilitzant l'algoritme CKY.
        Omple la taula dinàmica de CKY amb la frase donada.
        :param frase: Es tracta de la cadena que volem analitzar.
        :return: Retorna un boolean que inidica si la cadena es pot derivar o no.
        """
        
        if not frase:
            # Comprovem si la cadena buida és derivable (S -> ε)
            return self._comprovar_derivacio_buida()
        
        n = len(frase)
        # Crea taula triangular buida (aprofitem la propietat triangular de la taula CKY i ens estalviem memòria innecessària)
        taula = [[set() for _ in range(n - m)] for m in range(n)]

        # Omplim la primera fila (cas base): terminals
        for col in range(n):
            paraula = frase[col]
            for no_terminal, produccions in self.gramatica.items():
                for produccio, probabilitat in produccions:
                    # Comprovem les produccions terminals (A -> a)
                    if isinstance(produccio, str) and produccio == paraula:
                        taula[0][col].add((no_terminal, probabilitat, (paraula,), (0, col), None))
                    elif isinstance(produccio, tuple) and len(produccio) == 1 and produccio[0] == paraula:
                        taula[0][col].add((no_terminal, probabilitat, (paraula,), (0, col), None))
        
        # Omplim la resta de la taula (longitud 2 a n)
        for fila in range(1, n):  # longitud de la subcadena
            for diag in range(n - fila):
                col = diag + fila

                # Provem totes les possibles divisions de la subcadena
                for k in range(fila):       
                    
                    fila_dreta = fila - k - 1
                    col_dreta = diag + k + 1

                    part_diag = taula[k][diag]
                    part_col = taula[fila_dreta][col_dreta]
                    # Si alguna de les dues parts és buida, no podem continuar
                    if not part_diag or not part_col:
                        continue
                    
                    # Comprovem totes les regles de la gramàtica per produccions binàries
                    for no_terminal_diag in part_diag:
                        for no_terminal_col in part_col:
                            # Comprovem les produccions binàries (A -> BC)
                            clau = (no_terminal_diag[0], no_terminal_col[0])
                            if clau in self.regles_binaries:
                                for valor_no_terminal, probabilitat in self.regles_binaries[clau]:
                                    # Comprovar si ja existeix aquest no-terminal en la cel·la
                                    existeix = False
                                    for tupla_existent in taula[fila][diag]:
                                        if tupla_existent[0] == valor_no_terminal:
                                            # Si ja existeix, comparem probabilitats i mantenim el major
                                            if probabilitat * no_terminal_diag[1] * no_terminal_col[1] > tupla_existent[1]:
                                                taula[fila][diag].remove(tupla_existent)
                                                break
                                            else:
                                                existeix = True
                                                break
                                    if not existeix:
                                        # Las coordenadas deben ser en formato original (inicio, fin)
                                        coord_izq = (diag, diag + k)
                                        coord_der = (diag + k + 1, col)
                                        taula[fila][diag].add((valor_no_terminal, 
                                                            probabilitat * no_terminal_diag[1] * no_terminal_col[1], 
                                                            (no_terminal_diag[0], no_terminal_col[0]), 
                                                            coord_izq, 
                                                            coord_der))
        # Al final del método algoritme_pcky, cambia esta línea:
        self.crear_arbre_gramatical(taula)
        # Comprovem si el símbol arrel està present en alguna tupla de la cel·la final
        for tupla in taula[n-1][0]:
            if tupla[0] == self.simbol_arrel:
                return True
        return False
    
    def crear_arbre_gramatical(self, taula: List[List[Set[Tuple[str, float, Tuple[str,str], Tuple[int, int]]]]]) -> None:
        # Buscar la tupla con mayor probabilidad para el símbolo raíz en la celda final
        millor_tupla = None
        millor_probabilitat = 0
        
        # La celda final en tabla triangular es taula[n-1][0]
        for tupla in taula[len(taula) - 1][0]:
            if tupla[0] == self.simbol_arrel and tupla[1] > millor_probabilitat:
                millor_tupla = tupla
                millor_probabilitat = tupla[1]
        
        if millor_tupla:
            self.arbre_gramatical = self._construir_arbre(taula, len(taula) - 1, 0, self.simbol_arrel)
        else:
            self.arbre_gramatical = None

    def _construir_arbre(self, taula: List[List[Set[Tuple[str, float, Tuple[str,str], Tuple[int, int]]]]], fila: int, col: int, no_terminal: str) -> dict:
        """
        Construeix l'arbre gramatical a partir de la taula triangular de CKY.
        :param fila: Fila en la tabla triangular (longitud - 1)
        :param col: Columna en la tabla triangular (posición inicial)
        :param no_terminal: No terminal a buscar
        """
        # Buscar la tupla con mayor probabilidad para este no terminal
        millor_tupla = None
        millor_probabilitat = 0
        
        for tupla in taula[fila][col]:
            if tupla[0] == no_terminal and tupla[1] > millor_probabilitat:
                millor_tupla = tupla
                millor_probabilitat = tupla[1]
        
        if millor_tupla is None:
            return None
        
        if fila == 0:  # Caso terminal (fila 0 = longitud 1)
            # tupla[2] es (palabra,) para terminales
            return {
                'no_terminal': no_terminal, 
                'simbol': millor_tupla[2][0], 
                'fill': None,
                'probabilitat': millor_tupla[1]
            }
        else:
            # Caso no terminal: tupla[2] es (NT_izq, NT_der)
            # Necesitamos convertir las coordenadas originales a coordenadas triangulares
            coord_orig_izq = millor_tupla[3]  # (inicio, fin) del hijo izquierdo
            coord_orig_der = millor_tupla[4]  # (inicio, fin) del hijo derecho
            
            # Convertir coordenadas originales a coordenadas triangulares
            # Para hijo izquierdo: (inicio_orig, fin_orig) -> (fin_orig - inicio_orig, inicio_orig)
            fila_izq = coord_orig_izq[1] - coord_orig_izq[0]
            col_izq = coord_orig_izq[0]
            
            # Para hijo derecho: (inicio_orig, fin_orig) -> (fin_orig - inicio_orig, inicio_orig)
            fila_der = coord_orig_der[1] - coord_orig_der[0]
            col_der = coord_orig_der[0]
            
            fill_esquerra = self._construir_arbre(taula, fila_izq, col_izq, millor_tupla[2][0])
            fill_dreta = self._construir_arbre(taula, fila_der, col_der, millor_tupla[2][1])
            
            return {
                'no_terminal': no_terminal, 
                'simbol': millor_tupla[2], 
                'fill': [fill_esquerra, fill_dreta],
                'probabilitat': millor_tupla[1]
            }

    
    
    def display_arbre(self):
        """
        Mostra l'arbre gramatical de manera llegible.
        """
        if self.arbre_gramatical is None:
            print("No s'ha creat cap arbre gramatical.")
            return
        self._mostrar_arbre(self.arbre_gramatical, 0)

    def _mostrar_arbre(self, node: dict, depth: int):
        """
        Mostra un node de l'arbre gramatical de manera estètica i jeràrquica.
        :param node: Node de l'arbre a mostrar.
        :param depth: Profunditat del node en l'arbre.
        """
        if node is None:
            return
        
        prefix = "│   " * (depth - 1) + ("├── " if depth > 0 else "")
        
        if node['fill'] is None:
            # Terminal
            print(f"{prefix}\033[1;32m{node['no_terminal']}\033[0m → '\033[1;34m{node['simbol']}\033[0m' (p={node['probabilitat']:.2e})")
        else:
            # No terminal
            print(f"{prefix}\033[1;33m{node['no_terminal']}\033[0m (p={node['probabilitat']:.2e})")
            for fill in node['fill']:
                self._mostrar_arbre(fill, depth + 1)
        
    def _preprocessar_gramatica(self) -> Dict[Tuple[str, str], Set[tuple[str, float]]]:
        """ 
        Preprocessa la gramàtica per accés ràpid a les regles binàries.
        """
        regles_binaries = {}
        
        for no_terminal, produccions in self.gramatica.items():
            for produccio, probabilitat in produccions: 
                if isinstance(produccio, tuple) and len(produccio) == 2:  # Només regles binàries
                    clau = (produccio[0], produccio[1])
                    if clau not in regles_binaries:
                        regles_binaries[clau] = set()
                    regles_binaries[clau].add((no_terminal, probabilitat))

        return regles_binaries
    
    def _comprovar_derivacio_buida(self) -> bool:
        """ 
        Comprova si la cadena buida és derivable a partir del símbol d'inici. 
        """
        if self.simbol_arrel in self.gramatica:
            for produccio, _ in self.gramatica[self.simbol_arrel]:
                if produccio == '':
                    return True
        return False
    
    def __str__(self):
        """ Retorna una representació en cadena de la gramàtica carregada. """
        if self.gramatica is None:
            return "No s'ha carregat cap gramàtica."
        result = []
        for no_terminal, produccions in self.gramatica.items():
            prods = []
            for produccio, probabilitat in produccions:
                if isinstance(produccio, tuple):
                    prod_str = ''.join(produccio)
                else:
                    prod_str = str(produccio)
                prods.append(f"{prod_str} ({probabilitat})")
            result.append(f"{no_terminal} -> {' | '.join(prods)}")
        return "\n".join(result)

    

def create_grammar_g1():
    """
    Create the first example grammar G1 - CORREGIDA CON TUPLAS
    """
    return {
        'S': [('a', 0.3), (('X', 'A'), 0.2), (('A', 'X'), 0.4), ('b', 0.1)],
        'A': [(('R', 'B'), 1.0)],
        'B': [(('A', 'X'), 0.5), ('b', 0.3), ('a', 0.2)],
        'X': [('a', 1.0)],
        'R': [(('X', 'B'), 1.0)]
    }

def create_grammar_g2():
    """
    Create the second example grammar G2 - CORREGIDA CON TUPLAS
    """
    return {
        'S': [(('A', 'B'), 0.4), (('C', 'D'), 0.3), (('C', 'B'), 0.2), (('B', 'B'), 0.1)],
        'A': [(('B', 'C'), 0.7), ('a', 0.3)],
        'B': [(('A', 'C'), 0.6), ('b', 0.4)],
        'C': [(('D', 'D'), 0.8), ('b', 0.2)],
        'D': [(('B', 'A'), 1.0)]
    }
def create_grammar_g3():
    """
    Create the third example grammar G3:
    S → AB | CD
    A → aA | a
    B → bB | b
    C → cC | c
    D → dD | d
    """
    return {
        'S': [(('NP', 'VP'), 1.0)],  # S → NP VP
        'NP': [(('Det', 'N'), 0.7), (('Det', 'AN'), 0.3)],  # NP → Det N | Det AN
        'AN': [(('Adj', 'N'), 1.0)],  # AN → Adj N 
        'VP': [(('V', 'NP'), 1.0)],  # VP → V NP
        'Det': [('els', 1.0)],  # Det → els
        'N': [('carbassots', 0.5), ('pardimolls', 0.5)],  # N → carbassots | pardimolls
        'Adj': [('millors', 1.0)],  # Adj → millors
        'V': [('són', 1.0)]  # V → són
    }



def main():
    # Prova amb la primera gramàtica (G1)
    print("\nProva amb la gramàtica G1")
    
    parser = GramaticaProbabilistica(create_grammar_g1(), simbol_arrel='S')
    print(parser)
    frases_g1 = ["a", "b", "aa", "ab", "ba", "aba", "aaa", "bab", "abab"]
    for frase in frases_g1:
        print(f"Frase: '{frase}'", end=" -> ")
        print(parser.algoritme_pcky(frase))
    
    # Prova amb la segona gramàtica (G2)
    print("\nProva amb la gramàtica G2")
    
    parser = GramaticaProbabilistica(create_grammar_g2(),  simbol_arrel='S')
    print(parser)
    frases_g2 = ["ab", "bb", "a", "b", "abb", "bab", "abab", "bbbb", "aabb","abab"]
    for frase in frases_g2:
        print(f"Frase: '{frase}'", end=" -> ")
        print(parser.algoritme_pcky(frase))

    parser.display_arbre()

    # Prova amb la gramàtica de l'exemple
    print("\nProva amb la gramàtica de l'exemple")
    parser = GramaticaProbabilistica(create_grammar_g3(), simbol_arrel='S')
    print(parser)
    frases_xd = ["els carbassots són els millors pardimolls"]

    for frase in frases_xd:
        print(f"Frase: '{frase}'", end=" -> ")
        print(parser.algoritme_pcky(frase.split()))
    parser.display_arbre()

    
    


if __name__ == "__main__":
    main()