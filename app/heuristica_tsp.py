import numpy as np
from geopy.distance import geodesic

def heuristica_tsp(matriz):
    """Algoritmo heurístico para encontrar una ruta aproximada."""
    n = len(matriz)
    visitados = [False] * n
    ruta = [0]  # Empezamos en la primera ciudad
    visitados[0] = True

    for _ in range(n - 1):
        actual = ruta[-1]
        siguiente = min(
            [(i, matriz[actual][i]) for i in range(n) if not visitados[i]],
            key=lambda x: x[1]
        )[0]  # Ciudad más cercana no visitada

        ruta.append(siguiente)
        visitados[siguiente] = True

    ruta.append(0)  # Volver al inicio
    return ruta
