import pygame
import sys
import random
import networkx as nx
from collections import deque
import heapq

# ==== CONFIGURACIÓN ====
TAM_CELDA = 40  # Ajustado para que quepa mejor en la pantalla
matriz = [
    [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 1, 0, 1, 0, 0, 0],
    [0, 2, 0, 0, 1, 2, 1, 0, 1, 0],
    [0, 1, 1, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 2, 0, 1, 1, 0],
    [1, 1, 0, 0, 1, 1, 0, 0, 0, 0],
    [0, 0, 2, 0, 1, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 2, 0, 3],  # El queso está en (8, 9)
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
]

FILAS = len(matriz)
COLUMNAS = len(matriz[0])
ANCHO = COLUMNAS * TAM_CELDA
ALTO = FILAS * TAM_CELDA

BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
NARANJA = (255, 165, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
GRIS = (200, 200, 200)
AMARILLO = (255, 255, 0)  # Color visible para el texto

# ==== FUNCIONES ====

def crear_grafo_desde_matriz(matriz):
    G = nx.Graph()
    for i in range(FILAS):
        for j in range(COLUMNAS):
            if matriz[i][j] != 1:  # No es pared
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < FILAS and 0 <= nj < COLUMNAS and matriz[ni][nj] != 1:
                        G.add_edge((i, j), (ni, nj))
    return G

# Función para encontrar el queso
def encontrar_queso(matriz):
    for i in range(FILAS):
        for j in range(COLUMNAS):
            if matriz[i][j] == 3:
                return (i, j)
    return None

# Función para mover el queso (lo mueve aleatoriamente)
def mover_queso():
    pos_actual = encontrar_queso(matriz)
    posibles = [(pos_actual[0] + dx, pos_actual[1] + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
    random.shuffle(posibles)
    for ni, nj in posibles:
        if 0 <= ni < FILAS and 0 <= nj < COLUMNAS and matriz[ni][nj] == 0:
            matriz[pos_actual[0]][pos_actual[1]] = 0
            matriz[ni][nj] = 3
            break

# Función para mover los obstáculos (2)
def mover_obstaculos():
    posiciones = [(i, j) for i in range(FILAS) for j in range(COLUMNAS) if matriz[i][j] == 2]
    nuevas = []
    for i, j in posiciones:
        posibles = [(i + dx, j + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        random.shuffle(posibles)
        for ni, nj in posibles:
            if 0 <= ni < FILAS and 0 <= nj < COLUMNAS and matriz[ni][nj] == 0:
                matriz[i][j] = 0
                matriz[ni][nj] = 2
                nuevas.append((ni, nj))
                break

# ==== ALGORITMOS DE BÚSQUEDA ====

def bfs(grafo, inicio, objetivo):
    # Algoritmo de búsqueda en amplitud (BFS)
    padre = {inicio: None}
    cola = deque([inicio])
    while cola:
        nodo = cola.popleft()
        if nodo == objetivo:
            camino = []
            while nodo is not None:
                camino.append(nodo)
                nodo = padre[nodo]
            return camino[::-1]  # Invertir el camino para que empiece desde el inicio
        for vecino in grafo.neighbors(nodo):
            if vecino not in padre:
                padre[vecino] = nodo
                cola.append(vecino)
    return []

# Aquí puedes agregar las funciones DFS y A* de manera similar a BFS

# ==== PYGAME SETUP ====
pygame.init()
ventana = pygame.display.set_mode((ANCHO * 2, ALTO))  # Ventana doble, una para el laberinto y otra para el árbol
pygame.display.set_caption("Agente en Laberinto Dinámico")
clock = pygame.time.Clock()

# ==== INICIO ====
pos_agente = (0, 0)
grafo = crear_grafo_desde_matriz(matriz)
objetivo = encontrar_queso(matriz)
metodo_actual = "BFS"

# Verificar si hay un camino disponible
if pos_agente in grafo.nodes and objetivo in grafo.nodes:
    camino = bfs(grafo, pos_agente, objetivo)
    index_camino = 1
else:
    camino = None  # No hay camino posible por ahora

# Variable para verificar si el agente llegó al queso
llego_queso = False

# ==== DIBUJAR ÁRBOL DE BÚSQUEDA ====

def dibujar_arbol(grafo, camino, ventana_arbol):
    # Dibujar los nodos y aristas del árbol de búsqueda
    radio_nodo = 15
    distancia_x = 100
    distancia_y = 60
    nodos_pos = {}  # Almacenamos las posiciones de los nodos para dibujar

    for i, nodo in enumerate(camino):
        x_pos = 30 + (i % 4) * distancia_x
        y_pos = 30 + (i // 4) * distancia_y
        nodos_pos[nodo] = (x_pos, y_pos)
        pygame.draw.circle(ventana_arbol, AMARILLO, (x_pos, y_pos), radio_nodo)
        texto = pygame.font.Font(None, 24).render(str(nodo), True, NEGRO)
        ventana_arbol.blit(texto, (x_pos - radio_nodo, y_pos - radio_nodo))

    # Dibujar las aristas
    for i in range(len(camino) - 1):
        nodo_a = camino[i]
        nodo_b = camino[i + 1]
        pygame.draw.line(ventana_arbol, NEGRO, nodos_pos[nodo_a], nodos_pos[nodo_b], 2)

# ==== LOOP PRINCIPAL ====
running = True
while running:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False

    # Verificar si el agente llegó al queso
    if pos_agente == objetivo and not llego_queso:
        llego_queso = True  # El agente ha llegado al queso

    # Solo mover el agente si aún no llegó al queso
    if not llego_queso:
        # Actualizar entorno
        mover_obstaculos()
        mover_queso()

        # Actualizar la posición del queso
        objetivo = encontrar_queso(matriz)

        # Recalcular el camino hacia el nuevo queso
        grafo = crear_grafo_desde_matriz(matriz)
        if pos_agente in grafo.nodes and objetivo in grafo.nodes:
            camino = bfs(grafo, pos_agente, objetivo)
            index_camino = 1

        # Actualizar movimiento del agente
        if camino and index_camino < len(camino):
            pos_agente = camino[index_camino]
            index_camino += 1

    # Dibujar laberinto
    ventana.fill(GRIS)
    for i in range(FILAS):
        for j in range(COLUMNAS):
            x = j * TAM_CELDA
            y = i * TAM_CELDA
            valor = matriz[i][j]
            color = BLANCO
            if valor == 1:
                color = NEGRO
            elif valor == 2:
                color = AZUL
            elif valor == 3:
                color = NARANJA
            pygame.draw.rect(ventana, color, pygame.Rect(x, y, TAM_CELDA, TAM_CELDA))

    # Mostrar el agente
    pygame.draw.circle(ventana, ROJO, (pos_agente[1] * TAM_CELDA + TAM_CELDA // 2, pos_agente[0] * TAM_CELDA + TAM_CELDA // 2), TAM_CELDA // 4)

    # Mostrar el árbol de búsqueda en una ventana separada
    ventana_arbol = pygame.Surface((200, ALTO))  # Ventana secundaria para el árbol
    ventana_arbol.fill(BLANCO)
    pygame.draw.rect(ventana_arbol, NEGRO, pygame.Rect(0, 0, 200, ALTO), 3)

    # Dibujar el árbol
    if camino:
        dibujar_arbol(grafo, camino, ventana_arbol)

    # Blit del árbol en la ventana principal
    ventana.blit(ventana_arbol, (ANCHO, 0))

    pygame.display.flip()
    clock.tick(5)  # Controlar la velocidad del agente

pygame.quit()
sys.exit()
