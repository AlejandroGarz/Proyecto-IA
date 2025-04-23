import pygame
import sys
import random
import networkx as nx
from collections import deque
import heapq
from Busqueda import bfs as bfs_matrix, dfs, a_asterisco

# === INTERFAZ PRINCIPAL ===
def iniciar_simulacion():
    pygame.font.init()  # Asegura que el sistema de fuentes esté inicializado
    # ==== CONFIGURACIÓN DEL LABERINTO ====
    TAM_CELDA = 40  # Tamaño de cada celda en píxeles

    # Matriz inicial del laberinto: 
    # 0: camino libre, 1: pared, 2: enemigo, 3: queso
    matriz_original = [
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 2],
        [1, 0, 1, 0, 1, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 1, 0, 1, 1, 1, 1],
        [1, 0, 1, 1, 1, 0, 3, 0, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 1, 0, 1],
        [1, 1, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [2, 0, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    # Función para reiniciar el juego
    def resetear_juego():
        return [fila[:] for fila in matriz_original], (0, 0), "A*", False

    # Inicializamos variables
    matriz, pos_agente, metodo_actual, llego_queso = resetear_juego()

    FILAS = len(matriz)
    COLUMNAS = len(matriz[0])
    ANCHO = COLUMNAS * TAM_CELDA
    ALTO = FILAS * TAM_CELDA

    # Colores RGB
    BLANCO = (255, 255, 255)
    NEGRO = (0, 0, 0)
    NARANJA = (255, 165, 0)  # Queso
    ROJO = (255, 0, 0)       # Agente (ratón)
    AZUL = (0, 0, 255)       # Enemigos
    GRIS = (200, 200, 200)   # Fondo
    AMARILLO = (255, 255, 0) # Texto
    VERDE = (0, 200, 0)      # Botón

    # Crear grafo de celdas navegables (sin paredes)
    def crear_grafo_desde_matriz():
        G = nx.Graph()
        for i in range(FILAS):
            for j in range(COLUMNAS):
                if matriz[i][j] != 1:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < FILAS and 0 <= nj < COLUMNAS and matriz[ni][nj] != 1:
                            peso = 1
                            if matriz[ni][nj] == 2:
                                peso = 5  # Costo extra si hay enemigo en la celda
                            G.add_edge((i, j), (ni, nj), weight=peso)
        return G

    # Buscar la posición actual del queso (valor 3 en matriz)
    def encontrar_queso():
        for i in range(FILAS):
            for j in range(COLUMNAS):
                if matriz[i][j] == 3:
                    return (i, j)
        return None

    # El queso se mueve para alejarse del agente
    def mover_queso(pos_agente):
        pos_actual = encontrar_queso()
        posibles = [(pos_actual[0] + dx, pos_actual[1] + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
        mejor_opcion = pos_actual
        max_distancia = -1
        for ni, nj in posibles:
            if 0 <= ni < FILAS and 0 <= nj < COLUMNAS and matriz[ni][nj] == 0:
                distancia = abs(ni - pos_agente[0]) + abs(nj - pos_agente[1])
                if distancia > max_distancia:
                    max_distancia = distancia
                    mejor_opcion = (ni, nj)
        matriz[pos_actual[0]][pos_actual[1]] = 0
        matriz[mejor_opcion[0]][mejor_opcion[1]] = 3

    # Los enemigos buscan al agente y se mueven usando A*
    def mover_enemigos(pos_agente):
        enemigos = [(i, j) for i in range(FILAS) for j in range(COLUMNAS) if matriz[i][j] == 2]
        nuevos_enemigos = []
        for i, j in enemigos:
            camino, _ = a_asterisco(matriz, (i, j), pos_agente)
            if camino and len(camino) > 1:
                siguiente = camino[1]
                if matriz[siguiente[0]][siguiente[1]] == 0:
                    matriz[i][j] = 0
                    nuevos_enemigos.append(siguiente)
                else:
                    nuevos_enemigos.append((i, j))
            else:
                nuevos_enemigos.append((i, j))
        for x, y in nuevos_enemigos:
            if matriz[x][y] == 0:
                matriz[x][y] = 2

    # Ejecutar la técnica de búsqueda seleccionada
    def buscar_camino(metodo, matriz, inicio, fin):
        if metodo == "DFS":
            return dfs(matriz, inicio, fin)
        elif metodo == "BFS":
            return bfs_matrix(matriz, inicio, fin)
        elif metodo == "A*":
            return a_asterisco(matriz, inicio, fin)
        return None, None

    # ==== SETUP DE PYGAME ====
    ventana = pygame.display.set_mode((ANCHO * 2, ALTO))
    pygame.display.set_caption("Agente en Laberinto Dinámico")
    clock = pygame.time.Clock()
    boton_reset = pygame.Rect(ANCHO + 30, 60, 140, 40)

    # ==== BUCLE PRINCIPAL ====
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_reset.collidepoint(evento.pos):
                    matriz, pos_agente, metodo_actual, llego_queso = resetear_juego()

        if not llego_queso:
            mover_enemigos(pos_agente)  # Mueven los enemigos hacia el agente
            mover_queso(pos_agente)     # El queso se aleja del agente
            objetivo = encontrar_queso()
            grafo = crear_grafo_desde_matriz()

            # Calcular camino evitando enemigos (costo alto en esas celdas)
            if pos_agente in grafo.nodes and objetivo in grafo.nodes:
                try:
                    camino = nx.astar_path(grafo, pos_agente, objetivo, heuristic=lambda a, b: abs(a[0]-b[0]) + abs(a[1]-b[1]))
                except:
                    camino = []
                if camino and len(camino) > 1:
                    pos_agente = camino[1]

        # ==== DIBUJO DE PANTALLA ====
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

        # Dibuja al agente (ratón)
        pygame.draw.circle(ventana, ROJO, (pos_agente[1] * TAM_CELDA + TAM_CELDA // 2, pos_agente[0] * TAM_CELDA + TAM_CELDA // 2), TAM_CELDA // 4)

        # Texto técnica actual
        fuente = pygame.font.SysFont(None, 24)
        texto = fuente.render(f"Técnica: {metodo_actual}", True, (0, 0, 0))
        ventana.blit(texto, (ANCHO + 30, 20))

        # Botón de reinicio
        pygame.draw.rect(ventana, VERDE, boton_reset)
        texto_reset = fuente.render("Reiniciar", True, BLANCO)
        ventana.blit(texto_reset, (boton_reset.x + 20, boton_reset.y + 10))

        pygame.display.flip()
        clock.tick(5)
