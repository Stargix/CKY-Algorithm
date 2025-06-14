n = 5

taula = [ [set() for j in range(n - i)] for i in range(n) ]

for diagonal in reversed(range(n)):
    print(f"Diagonal {diagonal}: ", end="")
    print(" " * (diagonal * 6), end="")  # Añade espacios para alinear a la derecha
    for j in range(n - diagonal):
        i = j
        print(f"({i},{j + diagonal})|", end="")
    print()


print(taula)
for i in range(n):
    print('[', end="")
    for j in range(n - i):
        print(f"({i},{j + i})", end=", ")
    print(']', end=" ")



taula = [ [(i,j) for j in range(n - i)] for i in range(n) ]

taula = [ [(diag_index,_) for _ in range(n - diag_index)] for diag_index in range(n) ]

print(taula[2][1])