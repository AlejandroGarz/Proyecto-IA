from collections import deque
import heapq

# Movimiento en las 4 direcciones: arriba, abajo, izquierda, derecha
direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def es_valido(matriz, pos):
    x, y = pos
    return 0 <= x < len(matriz) and 0 <= y < len(matriz[0]) and matriz[x][y] != 1

#busqueda por amplitub
def bfs(matriz, inicio, objetivo):
    # Asegúrate de que el inicio y el objetivo sean válidos
    if not es_valido(matriz, inicio) or not es_valido(matriz, objetivo):
        return None, None  # Si no es válido, retornamos None para ambos valores

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
    # Asegúrate de que el inicio y el objetivo sean válidos
    if not es_valido(matriz, inicio) or not es_valido(matriz, objetivo):
        return None, None  # Si no es válido, retornamos None para ambos valores

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

def heuristica(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

#busquedad A*
def a_asterisco(matriz, inicio, objetivo):
    # Asegúrate de que el inicio y el objetivo sean válidos
    if not es_valido(matriz, inicio) or not es_valido(matriz, objetivo):
        return None, None  # Si no es válido, retornamos None para ambos valores

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
