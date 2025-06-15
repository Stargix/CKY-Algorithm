from typing import Dict, List, Set, Tuple, Union
from copy import deepcopy

class GramaticaProbabilistica():
    def __init__(self, normes_gramatica: Dict, simbol_arrel: str = 'S') -> None:

        self.gramatica = deepcopy(normes_gramatica)
        self.forma_normal_chomsky()  # Transformem la gramàtica a FNC
        self.regles_binaries = self._preprocessar_gramatica()
        self.simbol_arrel = simbol_arrel
        self.arbre_gramatical = None

    def algoritme_pcky(self, frase: Union[List[str], str]) -> Tuple[bool, float]:
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
            for no_terminal, produccions in list(self.gramatica.items()):
                for produccio, probabilitat in produccions:
                    # Comprovem les produccions terminals (A -> a)
                    if isinstance(produccio, str) and produccio == paraula:
                        taula[0][col].add((no_terminal, probabilitat, (paraula,), (0, col), None))
                    elif isinstance(produccio, list) and len(produccio) == 1 and produccio[0] == paraula:
                        taula[0][col].add((no_terminal, probabilitat, (paraula,), (0, col), None))
        
        # Omplim la resta de la taula (longitud 2 a n)
        for longitud in range(1, n):  # longitud de la subcadena
            for col_esq in range(n - longitud): # inici de la subcadena
                col = col_esq + longitud

                # Provem totes les possibles divisions de la subcadena
                for fila_esq in range(longitud): # longitud de la part esquerra
                    
                    fila_dre = longitud - fila_esq - 1
                    col_dre = col_esq + fila_esq + 1

                    part_esq = taula[fila_esq][col_esq]
                    part_dre = taula[fila_dre][col_dre]

                    # Si alguna de les dues parts és buida, no podem continuar
                    if part_esq and part_dre:
                        # Comprovem totes les regles de la gramàtica per produccions binàries
                        for no_terminal_esq in part_esq:
                            for no_terminal_dre in part_dre:
                                # Comprovem les produccions binàries (A -> BC)
                                clau = (no_terminal_esq[0], no_terminal_dre[0])

                                if clau in self.regles_binaries:
                                    for valor_no_terminal, probabilitat in self.regles_binaries[clau]:
                                        # Busquem si ja existeix aquest no-terminal en la cel·la
                                        tupla_existent = None
                                        for tupla in taula[longitud][col_esq]:
                                            if tupla[0] == valor_no_terminal:
                                                tupla_existent = tupla
                                                break
                                        
                                        # Calculem la nova probabilitat
                                        nova_probabilitat = probabilitat * no_terminal_esq[1] * no_terminal_dre[1]
                                        
                                        if tupla_existent is not None:
                                            # Si existeix, comprovem si la nova probabilitat és major
                                            if nova_probabilitat > tupla_existent[1]:
                                                taula[longitud][col_esq].remove(tupla_existent)
                                                # Agreguem la nova tupla amb la probabilitat actualitzada
                                                coord_esq = (col_esq, col_esq + fila_esq)
                                                coord_dre = (col_esq + fila_esq + 1, col)
                                                taula[longitud][col_esq].add((valor_no_terminal, 
                                                                            nova_probabilitat, 
                                                                            (no_terminal_esq[0], no_terminal_dre[0]), 
                                                                            coord_esq, 
                                                                            coord_dre))
                                        else:
                                            # No existeix, agreguem directament
                                            coord_esq = (col_esq, col_esq + fila_esq)
                                            coord_dre = (col_esq + fila_esq + 1, col)
                                            taula[longitud][col_esq].add((valor_no_terminal, 
                                                                        nova_probabilitat, 
                                                                        (no_terminal_esq[0], no_terminal_dre[0]), 
                                                                        coord_esq, 
                                                                        coord_dre))
                                    
        # Un cop omplerta la taula, creem l'arbre gramatical
        self.crear_arbre_gramatical(taula)
        # Comprovem si el símbol arrel està present en alguna tupla de la cel·la final
        for tupla in taula[n-1][0]:
            if tupla[0] == self.simbol_arrel:
                return (True, tupla[1])
        return (False, 0.0)
    
    def _preprocessar_gramatica(self) -> Dict[Tuple[str, str], Set[tuple[str, float]]]:
        """ 
        Preprocessa la gramàtica per accés ràpid a les regles binàries.
        """
        regles_binaries = {}
        
        for no_terminal, produccions in list(self.gramatica.items()):
            for produccio, probabilitat in produccions: 
                # Comprovem si la producció és una regla binària
                if isinstance(produccio, list) and len(produccio) == 2:
                    clau = (produccio[0], produccio[1])

                    if clau not in regles_binaries:
                        regles_binaries[clau] = set()
                    regles_binaries[clau].add((no_terminal, probabilitat)) 
                    # emmagatzemem el no-terminal i la probabilitat
        return regles_binaries
    
    def crear_arbre_gramatical(self, taula: List[List[Set[Tuple[str, float, Tuple[str,str], Tuple[int, int]]]]]) -> None:
        """
        Crea l'arbre gramatical a partir de la taula triangular generada per l'algoritme CKY.
        :param taula: Taula triangular generada per l'algoritme CKY.
        """
        # Buscar la tupla amb major probabilitat per al símbol arrel en la cel·la final
        millor_tupla = None
        millor_probabilitat = 0
        
        # La cel·la final a la taula triangular és taula[n-1][0]
        for tupla in taula[len(taula) - 1][0]:
            if tupla[0] == self.simbol_arrel and tupla[1] > millor_probabilitat:
                millor_tupla = tupla
                millor_probabilitat = tupla[1]
        
        if millor_tupla: 
            # Si hem trobat una tupla per al símbol arrel, construïm l'arbre gramatical
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
        # Buscar la tupla amb major probabilitat per al no terminal en la cel·la especificada
        millor_tupla = None
        millor_probabilitat = 0
        
        for tupla in taula[fila][col]:
            if tupla[0] == no_terminal and tupla[1] > millor_probabilitat:
                millor_tupla = tupla
                millor_probabilitat = tupla[1]
        
        if millor_tupla is None:
            return None
        
        if fila == 0:  # Es compleix per les regles terminals
            # La tupla conté (no_terminal, probabilitat, (simbol,), (inici, fi), None)
            return {
                'no_terminal': no_terminal, 
                'simbol': millor_tupla[2][0], 
                'fill': None,
                'probabilitat': millor_tupla[1]
            }
        
        # Cas de regles no terminals
        else: 
            # la tupla conté (no_terminal, probabilitat, (fill_esquerre, fill_dret), (inici_esq, fi_esq), (inici_dre, fi_dre))
            # Necessitem convertir les coordenades originals a coordenades triangulars
            coord_orig_esq = millor_tupla[3]
            coord_orig_dre = millor_tupla[4]
            
            # Convertim les coordenades a longitud i inici
            fila_esq = coord_orig_esq[1] - coord_orig_esq[0]
            col_esq = coord_orig_esq[0]
            
            fila_dre = coord_orig_dre[1] - coord_orig_dre[0]
            col_dre = coord_orig_dre[0]
            
            # Construïm els fills esquerre i dret de l'arbre
            fill_esquerra = self._construir_arbre(taula, fila_esq, col_esq, millor_tupla[2][0])
            fill_dreta = self._construir_arbre(taula, fila_dre, col_dre, millor_tupla[2][1])
            
            return {
                'no_terminal': no_terminal, 
                'simbol': millor_tupla[2], 
                'fill': [fill_esquerra, fill_dreta],
                'probabilitat': millor_tupla[1]
            }
    
    def display_arbre(self):
        """
        Mostra l'arbre gramatical de manera llegible.
        Utilitzem la funció _mostrar_arbre per imprimir l'arbre de manera jeràrquica.
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
            # Terminals
            print(f"{prefix}\033[1;32m{node['no_terminal']}\033[0m → '\033[1;34m{node['simbol']}\033[0m' (p={node['probabilitat']:.2e})")
        else:
            # No terminals
            print(f"{prefix}\033[1;33m{node['no_terminal']}\033[0m (p={node['probabilitat']:.2e})")
            for fill in node['fill']:
                self._mostrar_arbre(fill, depth + 1)
    
    def _comprovar_derivacio_buida(self) -> bool:
        """ 
        Comprova si la cadena buida és derivable a partir del símbol d'inici. 
        """
        if self.simbol_arrel in self.gramatica:
            for produccio, _ in self.gramatica[self.simbol_arrel]:
                if produccio == '' or produccio == []:
                    return True
        return False
    
    def forma_normal_chomsky(self) -> None:
        """
        Transforma la gramàtica a Forma Normal de Chomsky (FNC) per a gramàtiques probabilístiques.
        Les probabilitats es distribueixen proporcionalment quan es creen noves regles.
        """
        self._eliminar_produccions_buides_pcky()
        self._eliminar_regles_unitaries_pcky()
        self._convertir_regles_terminals_pcky()
        self._convertir_regles_llargues_pcky()

    def _generar_combinacions_pcky(self, produccio: List[str], buides: Set[str]) -> Set[Tuple[str]]:
        """
        Genera totes les combinacions possibles de produccions eliminant els no-terminals que són buits.
        :param produccio: Producció original.
        :param buides: Conjunt de no-terminals que poden derivar a la cadena buida.
        :return: Un conjunt de tuples amb les noves produccions.
        """
        if not produccio:
            return {tuple()}

        resultats = set()
        resultats.add(tuple(produccio))  # Sempre inclou la producció original

        for i in range(len(produccio)):  # Itera sobre cada símbol de la producció
            if produccio[i] in buides:
                sub_combinacions = self._generar_combinacions_pcky(produccio[:i] + produccio[i+1:], buides)
                resultats.update(sub_combinacions)  # Genera combinacions sense aquest símbol si és buit

        return resultats

    def _eliminar_produccions_buides_pcky(self):
        """
        Elimina produccions buides de la gramàtica (A -> ε) per gramàtiques probabilístiques.
        Aquesta funció identifica els no-terminals que poden derivar a la cadena buida i elimina les produccions que només contenen aquests no-terminals. 
        Per exemple, si tenim A -> ε i B -> A C, llavors B es converteix en B -> C, mantenint les probabilitats adequades.
        """
        # Troba els no-terminals que poden derivar a la cadena buida
        buides = {no_terminal for no_terminal, produccions in list(self.gramatica.items()) 
                  for produccio, probabilitat in produccions 
                  if produccio == '' or produccio == [] or produccio == [''] or produccio == ['ε']}
        
        canvi = True
        while canvi:
            canvi = False
            nous_buides = buides.copy()

            for no_terminal, produccions in list(self.gramatica.items()):
                for produccio, probabilitat in produccions:
                    if produccio and all(simbol in buides for simbol in produccio):
                        if no_terminal not in nous_buides:  # Si el no-terminal ja és buit, no cal afegir-lo de nou
                            nous_buides.add(no_terminal)
                            canvi = True

            buides = nous_buides

        # Genera noves produccions sense els buits
        nova_gramatica = {}
        for no_terminal, produccions in list(self.gramatica.items()):
            noves_produccions = {}
            
            for produccio, probabilitat in produccions:
                if not (produccio == '' or produccio == [] or produccio == [''] or produccio == ['ε']):  # Si la producció és buida, no cal afegir-la
                    combinacions = self._generar_combinacions_pcky(list(produccio), buides)
                    for combinacio in combinacions:
                        if combinacio and combinacio != ('ε',) and combinacio != ('',):
                            if combinacio not in noves_produccions:
                                noves_produccions[combinacio] = 0.0
                            noves_produccions[combinacio] += probabilitat  # Suma les probabilitats de combinacions idèntiques

            # Actualitza les produccions del no-terminal, eliminant les que són buides o iguals a "ε"
            nova_gramatica[no_terminal] = [(list(prod), prob) for prod, prob in noves_produccions.items()]
        
        self.gramatica = nova_gramatica

    def _eliminar_regles_unitaries_pcky(self):
        """
        Elimina regles unitàries de la gramàtica (A -> B) per gramàtiques probabilístiques.
        Aquesta funció transforma regles unitàries en regles que contenen les produccions de B, multiplicant les probabilitats.
        Per exemple, si tenim A -> B (p=0.5) i B -> C D (p=0.8), llavors A es converteix en A -> C D (p=0.4).
        """
        canviat = True
        while canviat:
            canviat = False
            nova_gramatica = {}
            
            for no_terminal, produccions in list(self.gramatica.items()):
                noves_produccions = []
                
                for produccio, probabilitat in produccions:
                    if len(produccio) == 1 and produccio[0] in self.gramatica:
                        # És una regla unitària - propaga les produccions del no-terminal referit
                        for sub_produccio, sub_probabilitat in self.gramatica[produccio[0]]:
                            nova_produccio = (sub_produccio, probabilitat * sub_probabilitat)
                            if nova_produccio not in noves_produccions:  # Evita duplicats
                                noves_produccions.append(nova_produccio)
                                canviat = True  # Si s'ha afegit una nova producció, marquem el canvi
                    else:
                        noves_produccions.append((produccio, probabilitat))  # Manté les produccions que no són unitàries
                
                nova_gramatica[no_terminal] = noves_produccions
            
            self.gramatica = nova_gramatica

    def _convertir_regles_terminals_pcky(self):
        """
        Converteix regles com (A -> ab) en regles no terminals separades (A -> T1 T2) 
        on Tn és un nou no-terminal (T1 -> a) (T2 -> b) per gramàtiques probabilístiques.

        Pressuposa que les regles terminals estàn escrites en minúscules.
        Manté les probabilitats originals en les noves regles creades.
        """
        contador = 1
        mapa_terminals = {}
        nova_gramatica = {}

        for no_terminal, produccions in list(self.gramatica.items()):
            noves_produccions = []

            for produccio, probabilitat in produccions:
                if len(produccio) > 1:
                    nova_produccio = []
                    
                    for simbol in produccio:
                        if simbol.islower():  # És una terminal en una regla llarga
                            if simbol not in mapa_terminals:
                                nou_no_terminal = f"T{contador}"  # Afegim un nou no-terminal per la regla
                                contador += 1
                                mapa_terminals[simbol] = nou_no_terminal
                                nova_gramatica[nou_no_terminal] = [([simbol], 1.0)]  # Afegim la regla terminal (Tn -> a)

                            nova_produccio.append(mapa_terminals[simbol])  # Afegim el no-terminal corresponent a la terminal
                        else:
                            nova_produccio.append(simbol)  # Si no és una terminal, l'afegim tal qual

                    noves_produccions.append((nova_produccio, probabilitat))
                else:
                    noves_produccions.append((produccio, probabilitat))

            nova_gramatica[no_terminal] = noves_produccions

        # Afegeix les regles terminals noves que no existien
        for terminal, nou_no_terminal in mapa_terminals.items():
            if nou_no_terminal not in nova_gramatica:
                nova_gramatica[nou_no_terminal] = [([terminal], 1.0)]

        self.gramatica = nova_gramatica

    def _convertir_regles_llargues_pcky(self):
        """
        Converteix regles llargues a regles binàries per gramàtiques probabilístiques, és a dir, transforma regles amb més de dos símbols en regles que només tenen dues parts.
        Per exemple, A -> B C D es converteix en A -> X1 D i X1 -> B C, on X1 és un nou no-terminal.
        Manté les probabilitats originals en les produccions finals.
        """
        contador = 1
        nova_gramatica = {}

        for no_terminal, produccions in list(self.gramatica.items()):
            noves_produccions = []

            for produccio, probabilitat in produccions:
                produccio_actual = list(produccio)
                
                while len(produccio_actual) > 2:
                    nou_no_terminal = f"X{contador}"  # Afegim un nou no-terminal per la regla
                    contador += 1
                    nova_gramatica[nou_no_terminal] = [([produccio_actual[0], produccio_actual[1]], 1.0)]  # Afegim la regla binària (Xn -> A B)
                    produccio_actual = [nou_no_terminal] + produccio_actual[2:]  # Actualitzem la producció per continuar amb la següent part

                noves_produccions.append((produccio_actual, probabilitat))  # Manté la producció final que ara té com a màxim dos símbols

            if no_terminal in nova_gramatica:
                nova_gramatica[no_terminal].extend(noves_produccions)
            else:
                nova_gramatica[no_terminal] = noves_produccions

        self.gramatica = nova_gramatica
    
    def __str__(self):
        """ Retorna una representació en cadena de la gramàtica carregada. """
        if self.gramatica is None:
            return "No s'ha carregat cap gramàtica."
        result = []
        for no_terminal, produccions in list(self.gramatica.items()):
            prods = []
            for produccio, probabilitat in produccions:
                if isinstance(produccio, list):
                    prod_str = ' '.join(produccio)
                else:
                    prod_str = str(produccio)
                prods.append(f"{prod_str} ({probabilitat})")
            result.append(f"{no_terminal} -> {' | '.join(prods)}")
        return "\n".join(result)
