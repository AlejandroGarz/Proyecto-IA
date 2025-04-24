from collections import deque
import heapq

# Movimiento en las 4 direcciones: arriba, abajo, izquierda, derecha
direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def es_valido(matriz, pos):
    filas = len(matriz)
    columnas = len(matriz[0])
    r, c = pos
    return 0 <= r < filas and 0 <= c < columnas and matriz[r][c] != 1

#busqueda por amplitub
def bfs(matriz, inicio, objetivo):
    if not es_valido(matriz, inicio) or not es_valido(matriz, objetivo):
        return None, None  

    visitado = set([inicio])
    cola = deque([(inicio, [inicio])])
    arbol = {}  # Para almacenar el árbol de búsqueda

    while cola:
        nodo, camino = cola.popleft()
        if nodo == objetivo:
            return camino, arbol
        for dx, dy in direcciones:
            vecino = (nodo[0] + dx, nodo[1] + dy)
            if es_valido(matriz, vecino) and vecino not in visitado:
                visitado.add(vecino)
                cola.append((vecino, camino + [vecino]))
                arbol[vecino] = nodo  # Guardamos de dónde vino el vecino

    return None, arbol  # Si no se encuentra camino, devolvemos None para ambos


#busqueda por profundidad
def dfs(matriz, inicio, objetivo):
    if not es_valido(matriz, inicio) or not es_valido(matriz, objetivo):
        return None, None 

    pila = [(inicio, [inicio])]
    visitado = set()
    arbol = {}

    while pila:
        nodo, camino = pila.pop()
        if nodo == objetivo:
            return camino, arbol
        if nodo in visitado:
            continue
        visitado.add(nodo)
        for dx, dy in direcciones:
            vecino = (nodo[0] + dx, nodo[1] + dy)
            if es_valido(matriz, vecino) and vecino not in visitado:
                pila.append((vecino, camino + [vecino]))
                arbol[vecino] = nodo  # Guardamos de dónde vino el vecino

    return None, arbol


def costo_uniforme(matriz, inicio, fin):
    filas = len(matriz)
    columnas = len(matriz[0])
    priority_queue = [(0, inicio, [inicio])] # (costo, nodo, camino)
    visitados = {inicio}
    arbol_busqueda = [inicio]

    while priority_queue:
        costo_actual, nodo_actual, camino_actual = heapq.heappop(priority_queue)
        if nodo_actual == fin:
            return camino_actual, arbol_busqueda

        fila, columna = nodo_actual
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nueva_fila, nueva_columna = fila + dr, columna + dc
            nuevo_nodo = (nueva_fila, nueva_columna)
            nuevo_costo = costo_actual + 1 # Costo de cada paso es 1 (puedes ajustarlo)

            if 0 <= nueva_fila < filas and 0 <= nueva_columna < columnas and matriz[nueva_fila][nueva_columna] != 1 and nuevo_nodo not in visitados:
                visitados.add(nuevo_nodo)
                nuevo_camino = list(camino_actual)
                nuevo_camino.append(nuevo_nodo)
                heapq.heappush(priority_queue, (nuevo_costo, nuevo_nodo, nuevo_camino))
                arbol_busqueda.append(nuevo_nodo)

    return None, arbol_busqueda

def heuristica(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

#busquedad avara
def avara(matriz, inicio, fin):
    filas = len(matriz)
    columnas = len(matriz[0])
    priority_queue = [(heuristica(inicio, fin), inicio, [inicio])] # (heurística, nodo, camino)
    visitados = {inicio}
    arbol_busqueda = [inicio]

    while priority_queue:
        _, nodo_actual, camino_actual = heapq.heappop(priority_queue)
        if nodo_actual == fin:
            return camino_actual, arbol_busqueda

        fila, columna = nodo_actual
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nueva_fila, nueva_columna = fila + dr, columna + dc
            nuevo_nodo = (nueva_fila, nueva_columna)

            if 0 <= nueva_fila < filas and 0 <= nueva_columna < columnas and matriz[nueva_fila][nueva_columna] != 1 and nuevo_nodo not in visitados:
                visitados.add(nuevo_nodo)
                nuevo_camino = list(camino_actual)
                nuevo_camino.append(nuevo_nodo)
                prioridad = heuristica(nuevo_nodo, fin)
                heapq.heappush(priority_queue, (prioridad, nuevo_nodo, nuevo_camino))
                arbol_busqueda.append(nuevo_nodo)

    return None, arbol_busqueda

#busquedad A*
def a_asterisco(matriz, inicio, objetivo):
    if not es_valido(matriz, inicio) or not es_valido(matriz, objetivo):
        return None, None 

    cola = [(0 + heuristica(inicio, objetivo), 0, inicio, [inicio])]
    visitado = set()
    arbol = {}

    while cola:
        f, costo, nodo, camino = heapq.heappop(cola)
        if nodo == objetivo:
            return camino, arbol
        if nodo in visitado:
            continue
        visitado.add(nodo)

        for dx, dy in direcciones:
            vecino = (nodo[0] + dx, nodo[1] + dy)
            if es_valido(matriz, vecino) and vecino not in visitado:
                nuevo_costo = costo + 1
                prioridad = nuevo_costo + heuristica(vecino, objetivo)
                heapq.heappush(cola, (prioridad, nuevo_costo, vecino, camino + [vecino]))
                arbol[vecino] = nodo  # Guardamos de dónde vino el vecino

    return None, arbol
