# ======== CFG en forma normal de Chomsky (CNF) ========

G1 = {
        "S": [["a"], ["X", "A"], ["A", "X"], ["b"]],
        "A": [["R", "B"]],
        "B": [["A", "X"], ["b"], ["a"]],
        "X": [["a"]],
        "R": [["X", "B"]]
     }

G2 = {
        "S": [["A", "B"], ["C", "D"], ["C", "B"], ["S", "S"]],
        "A": [["B", "C"], ["a"]],
        "B": [["S", "C"], ["b"]],
        "C": [["D", "D"], ["b"]],
        "D": [["B", "A"]]
     }

G3 = {
        "S": [["A", "B"]],
        "A": [["a", "A"], ["a"]],
        "B": [["b", "B"], ["b"]]
     }

# G4 extreta de l'exàmen final de PLH del 2023

G4 = {
        'S': [['NP', 'VP']],
        'NP': [['DT', 'NN'], ['DT', 'NNS'], ['groucho'], ['shot'], ['elephant'], ['NP', 'PP']],
        'PP': [['IN', 'NP']],
        'VP': [['VP', 'PP'], ['VP', 'NP'], ['shot']],
        'NN': [['shot'], ['elephant']],
        'NNS': [['pajamas']],
        'DT': [['an'], ['his']],
        'IN': [['in']]
     }

# ======== CFG sense forma normal de Chomsky (CNF) ========

G5 = {
        "S": [["A", "B"], []],  # S -> AB | ε
        "A": [["a", "A"], ["a"], []],  # A -> aA | a | ε
        "B": [["b", "B"], ["b"]]
     }

G6 = {
        "S": [["A", "B", "C"], ["a"]],
        "A": [["a", "A"], ["b"], []],  # A -> aA | b | ε
        "B": [["b", "B"], ["c"]],
        "C": [["c", "C"], ["d"], ["B"]]   # C -> cC | d | ε
     }

G7 = {
        'S': [['NP', 'VP']],
        'NP': [['Det', 'N'], ['Det', 'Adj', 'N']],
        'VP': [['V', 'NP']],
        'Det': [['les']],
        'N': [['llistes'], ['estructures']],
        'Adj': [['millors']],
        'V': [['són']]
     }

# G8 extreta de l'exàmen final de PLH del 2024

G8 = {
        'S': [['NP', 'VP']],
        'NP': [['PRP', 'NN'], ['PRP', 'NNS'], ['NNP'], ['NP', 'AP']],
        'VP': [['VBD', 'NP'], ['VP', 'AP']],
        'AP': [['VBG', 'PP']],
        'PP': [['IN', 'NP']],
        'NNP': [['john']],
        'PRP': [['your'], ['his']],
        'NN': [['brother']],
        'NNS': [['glasses']],
        'IN': [['with']],
        'VBD': [['saw']],
        'VBG': [['playing']]
     }

# ======== CFG amb probabilitats ========

G9 = {
        'S': [(['A', 'B'], 0.6), (['B', 'A'], 0.4)],
        'A': [(['a'], 0.7), (['A', 'A'], 0.3)],
        'B': [(['b'], 1.0)]
     }

G10 = {
        "S": [(["a"], 0.2), (["X", "A"], 0.3), (["A", "X"], 0.3), (["b"], 0.2)],
        "A": [(["R", "B"], 1.0)],
        "B": [(["A", "X"], 0.4), (["b"], 0.3), (["a"], 0.3)],
        "X": [(["a"], 1.0)],
        "R": [(["X", "B"], 1.0)]
      }

# G11 extreta de l'exàmen final de PLH del 2023

G11 = {
        'S': [(['NP', 'VP'], 1.0)],
        'NP': [(['DT', 'NN'], 0.4), (['DT', 'NNS'], 0.3), (['groucho'], 0.01), (['shot'], 0.03), (['elephant'], 0.04), (['NP', 'PP'], 0.2)],
        'PP': [(['IN', 'NP'], 1.0)],
        'VP': [(['VP', 'PP'], 0.5), (['VP', 'NP'], 0.4), (['shot'], 0.03)],
        'NN': [(['shot'], 0.02), (['elephant'], 0.03)],
        'NNS': [(['pajamas'], 0.02)],
        'DT': [(['an'], 0.2),(['his'], 0.1)],
        'IN': [(['in'], 0.1)]
     }

# G12 extreta de l'exàmen final de PLH del 2024

G12 = {
        'S': [(['NP', 'VP'], 1.0)],
        'NP': [(['PRP', 'NN'], 0.5), (['PRP', 'NNS'], 0.3), (['NNP'], 0.1), (['NP', 'AP'], 0.1)],
        'NNP': [(['john'], 1.0)],
        'PRP': [(['your'], 0.6), (['his'], 0.4)],
        'NN': [(['brother'], 1.0)],
        'NNS': [(['glasses'], 1.0)],
        'AP': [(['VBG', 'PP'], 1.0)],
        'PP': [(['IN', 'NP'], 1.0)],
        'IN': [(['with'], 1.0)],
        'VBD': [(['saw'], 1.0)],
        'VBG': [(['playing'], 1.0)],
        'VP': [(['VBD', 'NP'], 0.4), (['VP', 'AP'], 0.6)]
     }

frases_ab = ["a", "b", "aa", "ab", "ba", "aba", "aaa", "bab", "abab", "aaaabbbb"]

def processa_frases(frases: list) -> list:
    """
    Processa una llista de frases, convertint-les en llistes de paraules
    En el cas de frases de caràcters simples (a, b, etc.), 
    aquest preprocessament no és necessari ja que els strings ja es comporten d'aquesta manera.
    """
    return [f.split() for f in frases]

frases_lst = [
        "les llistes són les millors estructures",
        "les llistes són les millors",
        "les llistes són estructures",
        "les estructures són les millors llistes",
]

frases_2023 = [
        "his pajamas",
        "groucho in pajamas",
        "elephant in pajamas",
        "groucho shot an elephant in his pajamas"
]

frases_2024 = [
        "john saw your brother",
        "john saw his glasses",
        "john playing with your brother",
        "john saw your brother playing with his glasses"
]

frases_lst, frases_2023, frases_2024 = map(processa_frases, [frases_lst, frases_2023, frases_2024])

gramatiques_simples = [(G1, frases_ab), (G2, frases_ab), (G3, frases_ab), (G4, frases_2023)]
gramatiques_no_FNC = [(G5, frases_ab), (G6, frases_ab), (G7, frases_lst), (G8, frases_2024)]
gramatiques_probabilistes = [(G9, frases_ab), (G10, frases_ab), (G11, frases_2023), (G12, frases_2024)]