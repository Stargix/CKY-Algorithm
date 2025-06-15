from gramatiques import gramatiques_simples
from main_cky import Gramatica

for gramatica in gramatiques_simples:
    print(f"\nProva amb la gramàtica {gramatica}")
    
    Gram = Gramatica(gramatica)
    print(Gram)
    
    for frase in ["ab", "bb", "a", "b", "abb", "bab", "abab", "bbbb", "aabb"]:
        print(f"Frase: '{frase}'", end=" -> ")
        print(Gram.algoritme_cky(frase))