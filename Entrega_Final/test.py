from gramatiques import gramatiques_simples, gramatiques_no_FNC, gramatiques_probabilistes
from main_cky import Gramatica
from extensio_1 import GramaticaFNC
from extensio_2 import GramaticaProbabilistica

def display_frases(gramatica, frases):
    """
    Mostra les frases i el resultat de l'algoritme CKY per a una gramàtica donada, en el cas de tenir una llista de frases, les concatena per simplificar la visualització
    """
    for frase in frases:
        frase_junt = frase
        if isinstance(frase, list):
            frase_junt = " ".join(frase)
        print(f"Frase: '{frase_junt}'", end=" -> ")
        print(gramatica.algoritme_cky(frase))

def test_cky():
    """
    Funció per provar l'algoritme CKY amb diferents gramàtiques i frases.
    """
    
    for gramatica, paraules in gramatiques_no_FNC:
        print(f"\nProva amb la gramàtica:\n")
        
        Gram = Gramatica(gramatica)
        print(Gram, end="\n\n")
        
        display_frases(Gram, paraules)

def test_fnc(cky=False):
    """
    Funció per provar la conversió a Forma Normal de Chomsky (FNC) i l'algoritme CKY amb gramàtiques en FNC.
    """
    
    for gramatica, paraules in gramatiques_no_FNC:
        print(f"\nProva amb la gramàtica en FNC:\n")
        
        Gram = Gramatica(gramatica)
        GramFNC = GramaticaFNC(gramatica)
        print(Gram, end="\n\n")
        print("Gramatica FNC:")
        print(GramFNC, end="\n\n")
        
        if cky:
            display_frases(GramFNC, paraules)

def test_pcky():
    """
    Funció per provar l'algoritme PCKY amb gramàtiques probabilístiques.
    """
    
    for gramatica, paraules in gramatiques_probabilistes:
        print(f"\nProva amb la gramàtica probabilística:\n")
        
        GramProb = GramaticaProbabilistica(gramatica)
        print(GramProb, end="\n\n")

        for frase in paraules:
            frase_junt = frase
            if isinstance(frase, list):
                frase_junt = " ".join(frase)
            print(f"Frase: '{frase_junt}'", end=" -> ")
            resultat, probabilitat = GramProb.algoritme_pcky(frase)
            if resultat:
                probabilitat = f"{probabilitat:5f}"
            print(f"{resultat}, prob: {probabilitat}")

            if resultat:
                print()
                GramProb.display_arbre()
                print()

if __name__ == "__main__":
    bucle = True
    while bucle:
        print("\nSelecciona una opció:")
        print("1. Test de l'algoritme CKY")
        print("2. Test de la conversió a FNC(Extensió 1)")
        print("3. Test de la conversió a FNC i l'algoritme CKY (Extensió 1 + base)")
        print("4. Test de l'algoritme PCKY (Extensió 2)")
        print("5. Tots els tests (CKY, FNC i PCKY)")
        print("6. Sortir")
        opcio = input("Introdueix el número de l'opció: ")

        if opcio == "1":
            print("Test de l'algoritme CKY:")
            test_cky()
        elif opcio == "2":
            print("\nTest de la conversió a FNC")
            test_fnc(cky=False)
        elif opcio == "3":
            print("\nTest de la conversió a FNC i l'algoritme CKY:")
            test_fnc(cky=True)
        elif opcio == "4":
            print("\nTest de l'algoritme PCKY:")
            test_pcky()
        elif opcio == "5":
            print("\nRealitzant tots els tests:")
            print("Test de l'algoritme CKY:")
            test_cky()
            print("\nTest de la conversió a FNC:")
            test_fnc(cky=True)
            print("\nTest de l'algoritme PCKY:")
            test_pcky()
        elif opcio == "6":
            print("Sortint...")
            bucle = False
        else:
            print("Opció no vàlida. Torna-ho a intentar.")