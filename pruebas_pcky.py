import typing
from typing import Dict, List, Set, Tuple

class GramaticaProbabilistica():
    def __init__(self, normes_gramatica: Set, simbol_arrel: str = 'S') -> None:
        self.gramatica = normes_gramatica
        self.regles_binaries = self._preprocessar_gramatica()
        self.simbol_arrel = simbol_arrel
        
    def algoritme_pcky(self, frase: str) -> bool:
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
        # Crear tabla como diccionario - CORREGIDO
        taula = [[set() for _ in range(n)] for _ in range(n)]

        # Omplim la primera fila (cas base): terminals
        for col in range(n):
            paraula = frase[col]
            for no_terminal, produccions in self.gramatica.items():
                for produccio, probabilitat in produccions:
                    # Comprovem les produccions terminals (A -> a)
                    if len(produccio) == 1 and produccio[0] == paraula:
                        taula[col][col].add({'no_terminal': no_terminal, 'probabilitat':probabilitat, 'coordenada': (col, col)})
        
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
                            clau = (no_terminal_diag['no_terminal'], no_termina_col['no_terminal'])
                            if clau in self.regles_binaries:
                                for clau_no_terminal, probabilitat in self.regles_binaries[clau]:
                                    # Afegim el no-terminal a la taula
                                    taula[diag][col].add({'no_terminal': clau_no_terminal, 'probabilitat': probabilitat * no_terminal_diag['probabilitat'] * no_termina_col['probabilitat'], 'coordenada': (diag, col)})
                                

        return self.simbol_arrel in taula[0][n-1]
    
                
    def _preprocessar_gramatica(self) -> Dict[Tuple[str, str], Set[tuple[str, float]]]:
        """ 
        Preprocessa la gramàtica per accés ràpid a les regles binàries.
        Aquesta funció crea un diccionari on les claus són tuples (esq, dre) i els valors són conjunts de no-terminals.
        """
        regles_binaries = {}  # Diccionari on (esq, dre) -> {no_terminal}
        
        for no_terminal, produccions in self.gramatica.items():
            for produccio, probabilitat in produccions: 
                if len(produccio) == 2:  # Només regles binarias
                    clau = (produccio[0], produccio[1])
                    if clau not in regles_binaries:
                        regles_binaries[clau] = set()
                    regles_binaries[clau].add((no_terminal,probabilitat))

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
    
    def forma_normal_chomsky(self) -> bool:
        """
        Transforma la gramàtica a Forma Normal de Chomsky (FNC).
        :return: Retorna True si la transformació s'ha completat correctament.
        """
        # 1. Eliminar producciones buides (A -> ε)
        self._eliminar_produccions_buides()
        # 2. Eliminar regles unitàries (A -> B)
        self._eliminar_regles_unitaries()
        # 3. Convertir regles llargues a regles binàries (A -> BC...Z)
        self._convertir_regles_llargues()
        # 4. Assegurar que les regles terminals siguin A -> a
        self._convertir_regles_terminals()

        return True

    def _eliminar_produccions_buides(self):
        """
        Elimina produccions buides (A -> ε) excepte per al símbol d'inici.
        """
        produccions_buides = set()
        
        # Identificar no terminales que producen ε
        for no_terminal, produccions in self.gramatica.items():
            for produccio in produccions:
                if produccio == ["ε"]:
                    produccions_buides.add(no_terminal)

        # Eliminar producciones ε y ajustar las demás reglas
        for no_terminal in self.gramatica:
            noves_produccions = set()
            for produccio in self.gramatica[no_terminal]:
                if any(nt in produccions_buides for nt in produccio):
                    # Generar nuevas combinaciones sin los no terminales que producen ε
                    combinacions = self._generar_combinacions(produccio, produccions_buides)
                    noves_produccions.update(combinacions)
                else:
                    noves_produccions.add(tuple(produccio))
            self.gramatica[no_terminal] = list(noves_produccions)

        # Eliminar ε de las producciones
        for no_terminal in produccions_buides:
            self.gramatica[no_terminal] = [
                produccio for produccio in self.gramatica[no_terminal] if produccio != ["ε"]
            ]

    def _eliminar_regles_unitaries(self):
        """Elimina reglas unitarias (A -> B)."""
        for no_terminal in list(self.gramatica.keys()):
            unitaries = [p[0] for p in self.gramatica[no_terminal] if len(p) == 1 and p[0] in self.gramatica]
            while unitaries:
                unitary = unitaries.pop()
                self.gramatica[no_terminal].remove([unitary])
                for produccio in self.gramatica[unitary]:
                    if produccio not in self.gramatica[no_terminal]:
                        self.gramatica[no_terminal].append(produccio)
                        if len(produccio) == 1 and produccio[0] in self.gramatica:
                            unitaries.append(produccio[0])

    def _convertir_regles_llargues(self):
        """Convierte reglas largas (A -> BC...Z) en reglas binarias."""
        contador = 1
        for no_terminal in list(self.gramatica.keys()):
            noves_produccions = []
            for produccio in self.gramatica[no_terminal]:
                while len(produccio) > 2:
                    # Crear un nuevo no terminal para dividir la regla
                    nou_no_terminal = f"X{contador}"
                    contador += 1
                    self.gramatica[nou_no_terminal] = [[produccio[0], produccio[1]]]
                    produccio = [nou_no_terminal] + produccio[2:]
                noves_produccions.append(produccio)
            self.gramatica[no_terminal] = noves_produccions

    def _convertir_regles_terminals(self):
        """Asegura que las reglas terminales sean de la forma A -> a."""
        contador = 1
        terminals_map = {}
        for no_terminal in list(self.gramatica.keys()):
            noves_produccions = []
            for produccio in self.gramatica[no_terminal]:
                if len(produccio) > 1:
                    nova_produccio = []
                    for simbol in produccio:
                        if simbol.islower():  # Es un terminal
                            if simbol not in terminals_map:
                                nou_no_terminal = f"T{contador}"
                                contador += 1
                                terminals_map[simbol] = nou_no_terminal
                                self.gramatica[nou_no_terminal] = [[simbol]]
                            nova_produccio.append(terminals_map[simbol])
                        else:
                            nova_produccio.append(simbol)
                    noves_produccions.append(nova_produccio)
                else:
                    noves_produccions.append(produccio)
            self.gramatica[no_terminal] = noves_produccions
        
        
        
    
    def __str__(self):
        """ Retorna una representació en cadena de la gramàtica carregada. """
        if self.gramatica is None:
            return "No s'ha carregat cap gramàtica."
        return "\n".join(f"{no_terminal} -> {', '.join(produccions)}" for no_terminal, produccions in self.gramatica.items())
    

    

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
        'S': [('a', 0.3), ('XA', 0.2), ('AX', 0.4), ('b', 0.1)],
        'A': [('RB', 1.0)],
        'B': [('AX', 0.5), ('b', 0.3), ('a', 0.2)],
        'X': [('a', 1.0)],
        'R': [('XB', 1.0)]
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
        'S': [('AB', 0.4), ('CD', 0.3), ('CB', 0.2), ('SS', 0.1)],
        'A': [('BC', 0.7), ('a', 0.3)],
        'B': [('SC', 0.6), ('b', 0.4)],
        'C': [('DD', 0.8), ('b', 0.2)],
        'D': [('BA', 1.0)]
    }