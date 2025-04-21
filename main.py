#libreria:
#pip install networkx
#pip install pygame

#entorno virtual para instalarlo:
#python3 -m venv venv
#source venv/bin/activate

import networkx as nx

def crear_grafo_desde_matriz(matriz):
    G = nx.Graph()
    filas = len(matriz)
    columnas = len(matriz[0])

    for i in range(filas):
        for j in range(columnas):
            if matriz[i][j] != 1:  # no es pared
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < filas and 0 <= nj < columnas and matriz[ni][nj] != 1:
                        G.add_edge((i, j), (ni, nj))

    return G
