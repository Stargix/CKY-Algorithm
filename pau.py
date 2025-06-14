word = "example"
n = len(word)

# Crear tabla como diccionario - CORREGIDO
taula = {}
for i in range(n):
    for j in range(i, n):  # j empieza en i, no en 0
        taula[(i, j)] = set()

print("Claves de la tabla:")
print(sorted(taula.keys()))

print(taula.keys())


for d in range(n-1, -1, -1):
    line = f"Fila {d}: "
    line += " " * (d * 6)  # Añade espacios para alinear a la derecha
    pairs = []
    for i in range(n - d):
        j = i + d
        pairs.append(f"{taula[i,j]}")
    line += "|".join(pairs)
    print(line)



for fila in range(1, n):  # longitud de la subcadena
    for diag in range(n - fila):
        col = diag + fila
        print(f"({diag},{col})", end="|")