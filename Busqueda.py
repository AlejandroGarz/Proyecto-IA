from collections import deque
import heapq

def bfs(grafo, inicio, objetivo):
    visitado = set()
    cola = deque([(inicio, [inicio])])

    while cola:
        nodo, camino = cola.popleft()
        if nodo == objetivo:
            return camino
        for vecino in grafo.neighbors(nodo):
            if vecino not in visitado:
                visitado.add(vecino)
                cola.append((vecino, camino + [vecino]))
    return None

def dfs(grafo, inicio, objetivo):
    pila = [(inicio, [inicio])]
    visitado = set()

    while pila:
        nodo, camino = pila.pop()
        if nodo == objetivo:
            return camino
        if nodo in visitado:
            continue
        visitado.add(nodo)
        for vecino in grafo.neighbors(nodo):
            if vecino not in visitado:
                pila.append((vecino, camino + [vecino]))
    return None

def heuristica(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_estrella(grafo, inicio, objetivo):
    cola = [(0 + heuristica(inicio, objetivo), 0, inicio, [inicio])]
    visitado = set()

    while cola:
        f, costo, nodo, camino = heapq.heappop(cola)
        if nodo == objetivo:
            return camino
        if nodo in visitado:
            continue
        visitado.add(nodo)

        for vecino in grafo.neighbors(nodo):
            if vecino not in visitado:
                nuevo_costo = costo + 1
                prioridad = nuevo_costo + heuristica(vecino, objetivo)
                heapq.heappush(cola, (prioridad, nuevo_costo, vecino, camino + [vecino]))

    return None


