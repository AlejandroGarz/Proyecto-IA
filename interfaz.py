import pygame
import sys
import random
import networkx as nx
from collections import deque
import heapq
from Busqueda import bfs as bfs_matrix, dfs, costo_uniforme, avara, a_asterisco

# === CONSTANTES ===
ANCHO = 600
ALTO = 400
GRIS = (200, 200, 200)
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
NARANJA = (255, 165, 0)

# === INTERFAZ PRINCIPAL ===
def iniciar_simulacion():
    pygame.font.init()
    TAM_CELDA = 40
    FILAS_INICIAL = 10
    COLUMNAS_INICIAL = 10

    global FILAS, COLUMNAS, matriz_configuracion, pos_agente, llego_queso, costo_total_agente, metodo_actual

    tecnicas_seleccionadas = ["A*"]
    metodo_actual = tecnicas_seleccionadas[0] if tecnicas_seleccionadas else "A*"

    def generar_matriz_inicial(filas, columnas, num_paredes=45, num_enemigos=3, queso_pos=None):
        matriz = [[0 for _ in range(columnas)] for _ in range(filas)]
        paredes_colocadas = 0
        while paredes_colocadas < num_paredes:
            r, c = random.randrange(filas), random.randrange(columnas)
            if matriz[r][c] == 0 and (r != 0 or c != 0):
                matriz[r][c] = 1
                paredes_colocadas += 1
        matriz[0][0] = 4
        if queso_pos:
            if 0 <= queso_pos[0] < filas and 0 <= queso_pos[1] < columnas and matriz[queso_pos[0]][queso_pos[1]] == 0:
                matriz[queso_pos[0]][queso_pos[1]] = 3
            else:
                while True:
                    r, c = random.randrange(filas), random.randrange(columnas)
                    if matriz[r][c] == 0 and (r != 0 or c != 0):
                        matriz[r][c] = 3
                        break
        else:
            while True:
                r, c = random.randrange(filas), random.randrange(columnas)
                if matriz[r][c] == 0 and (r != 0 or c != 0):
                    matriz[r][c] = 3
                    break
        enemigos_colocados = 0
        while enemigos_colocados < num_enemigos:
            r, c = random.randrange(filas), random.randrange(columnas)
            if matriz[r][c] == 0 and (r != 0 or c != 0):
                matriz[r][c] = 2
                enemigos_colocados += 1
        return matriz
    
    def resetear_juego(filas, columnas, matriz_inicial, tecnicas_seleccionadas):
        agente_pos = None
        queso_pos = None
        nueva_matriz = [fila[:] for fila in matriz_inicial]
        for i in range(filas):
            for j in range(columnas):
                if nueva_matriz[i][j] == 4:
                    agente_pos = (i, j)
                    nueva_matriz[i][j] = 0
                elif nueva_matriz[i][j] == 3:
                    queso_pos = (i, j)
        if agente_pos is None:
            agente_pos = (0, 0)
        if queso_pos is None:
            for i in range(filas):
                for j in range(columnas):
                    if nueva_matriz[i][j] == 0:
                        queso_pos = (i, j)
                        nueva_matriz[i][j] = 3
                        break
                if queso_pos:
                    break
        return nueva_matriz, agente_pos, tecnicas_seleccionadas[0] if tecnicas_seleccionadas else "A*", False, 0

    FILAS, COLUMNAS = FILAS_INICIAL, COLUMNAS_INICIAL
    matriz_configuracion = generar_matriz_inicial(FILAS, COLUMNAS)
    pos_agente = (0, 0)
    llego_queso = False
    costo_total_agente = 0
    juego_iniciado = False
    modo_queso_huida = True

    config_activa = True
    input_filas = pygame.Rect(ANCHO + 20, 50, 80, 25)
    input_columnas = pygame.Rect(ANCHO + 20, 90, 80, 25)
    texto_filas = str(FILAS_INICIAL)
    texto_columnas = str(COLUMNAS_INICIAL)
    color_activo = pygame.Color('lightskyblue3')
    color_inactivo = pygame.Color('grey')
    color_filas = color_inactivo
    color_columnas = color_inactivo
    activo_filas = False
    activo_columnas = False
    boton_generar = pygame.Rect(ANCHO + 20, 130, 150, 25)
    botones_tecnicas = {}
    tecnicas_disponibles_lista = ["BFS", "DFS", "Costo Uniforme", "Avara", "A*"]
    y_offset_tecnicas = 170
    for i, tecnica in enumerate(tecnicas_disponibles_lista):
        rect = pygame.Rect(ANCHO + 20, y_offset_tecnicas + i * 30, 180, 25)
        botones_tecnicas[tecnica] = (rect, True)
    boton_inicio = pygame.Rect(ANCHO + 20, y_offset_tecnicas + len(botones_tecnicas) * 30 + 20, 100, 25)
    boton_queso_huir = pygame.Rect(ANCHO + 20, boton_inicio.bottom + 15, 120, 25)
    boton_queso_aleatorio = pygame.Rect(ANCHO + 150, boton_inicio.bottom + 15, 120, 25)

    def crear_grafo_desde_matriz(current_matriz):
        G = nx.Graph()
        for i in range(FILAS):
            for j in range(COLUMNAS):
                if current_matriz[i][j] != 1:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < FILAS and 0 <= nj < COLUMNAS and current_matriz[ni][nj] != 1:
                            peso = 1
                            if current_matriz[ni][nj] == 2:
                                peso = 5
                            G.add_edge((i, j), (ni, nj), weight=peso)
        return G

    def encontrar_queso(current_matriz):
        for i in range(FILAS):
            for j in range(COLUMNAS):
                if current_matriz[i][j] == 3:
                    return (i, j)
        return None

    def mover_queso_huir(pos_agente, current_matriz):
        if random.randint(0, 100) < 50: # El queso solo se mueve con un 50% de probabilidad
            pos_actual = encontrar_queso(current_matriz)
            if pos_actual:
                posibles = [(pos_actual[0] + dx, pos_actual[1] + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
                mejor_opcion = pos_actual
                max_distancia = -1
                for ni, nj in posibles:
                    if 0 <= ni < FILAS and 0 <= nj < COLUMNAS and current_matriz[ni][nj] == 0:
                        distancia = abs(ni - pos_agente[0]) + abs(nj - pos_agente[1])
                        if distancia > max_distancia:
                            max_distancia = distancia
                            mejor_opcion = (ni, nj)
                if mejor_opcion != pos_actual: # Solo mover si se encontró una mejor opción
                    current_matriz[pos_actual[0]][pos_actual[1]] = 0
                    current_matriz[mejor_opcion[0]][mejor_opcion[1]] = 3
        return current_matriz

    def mover_queso_aleatorio(current_matriz):
        pos_actual = encontrar_queso(current_matriz)
        if pos_actual:
            posibles = [(pos_actual[0] + dx, pos_actual[1] + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
            random.shuffle(posibles)
            for ni, nj in posibles:
                if 0 <= ni < FILAS and 0 <= nj < COLUMNAS and current_matriz[ni][nj] == 0:
                    current_matriz[pos_actual[0]][pos_actual[1]] = 0
                    current_matriz[ni][nj] = 3
                    break
        return current_matriz

    def mover_enemigos(pos_agente, current_matriz, current_metodo):
        enemigos = [(i, j) for i in range(FILAS) for j in range(COLUMNAS) if current_matriz[i][j] == 2]
        nuevos_enemigos = []
        for i, j in enemigos:
            inicio = (i, j)
            fin = pos_agente
            camino, _ = buscar_camino(current_metodo, current_matriz, inicio, fin)
            if camino and len(camino) > 1:
                siguiente = camino[1]
                if current_matriz[siguiente[0]][siguiente[1]] == 0:
                    current_matriz[i][j] = 0
                    nuevos_enemigos.append(siguiente)
                else:
                    nuevos_enemigos.append((i, j))
            else:
                nuevos_enemigos.append((i, j))
        for x, y in nuevos_enemigos:
            if current_matriz[x][y] == 0:
                current_matriz[x][y] = 2
        return current_matriz

    def buscar_camino(metodo, current_matriz, inicio, fin):
        #limite = 50 #limite de pasos

        if metodo == "BFS":
            return bfs_matrix(current_matriz, inicio, fin)
        elif metodo == "DFS":
            return dfs(current_matriz, inicio, fin)#, limite)
        elif metodo == "Costo Uniforme":
            return costo_uniforme(current_matriz, inicio, fin)
        elif metodo == "Avara":
            return avara(current_matriz, inicio, fin)
        elif metodo == "A*":
            return a_asterisco(current_matriz, inicio, fin)
        
        return None, None

    def mover_pared_aleatorio(current_matriz):
        paredes = [(i, j) for i in range(FILAS) for j in range(COLUMNAS) if current_matriz[i][j] == 1]
        espacios_vacios = [(i, j) for i in range(FILAS) for j in range(COLUMNAS) if current_matriz[i][j] == 0]
        if paredes and espacios_vacios:
            random.shuffle(paredes)
            random.shuffle(espacios_vacios)
            pared_a_mover = paredes[0]
            nueva_posicion = espacios_vacios[0]
            current_matriz[pared_a_mover[0]][pared_a_mover[1]] = 0
            current_matriz[nueva_posicion[0]][nueva_posicion[1]] = 1
        return current_matriz

    def dibujar_arbol(grafo, camino, ventana_arbol):
        radio_nodo = 15
        distancia_x = 80
        distancia_y = 50
        nodos_pos = {}
        if camino:
            for i, nodo in enumerate(camino):
                x_pos = 20 + (i % 5) * distancia_x
                y_pos = 30 + (i // 5) * distancia_y
                nodos_pos[nodo] = (x_pos, y_pos)
                pygame.draw.circle(ventana_arbol, AMARILLO, (x_pos, y_pos), radio_nodo)
                texto = pygame.font.Font(None, 18).render(str(nodo), True, NEGRO)
                texto_rect = texto.get_rect(center=(x_pos, y_pos))
                ventana_arbol.blit(texto, texto_rect)
                if i > 0 and camino[i-1] in nodos_pos:
                    pygame.draw.line(ventana_arbol, VERDE, nodos_pos[camino[i-1]], nodos_pos[nodo], 2)

    juego_iniciado = False
    modo_queso_huida = True
    camino = None  # Inicializar la variable camino aquí
    
    # ==== SETUP DE PYGAME ====
    ANCHO_TOTAL = ANCHO + 300
    ventana = pygame.display.set_mode((ANCHO_TOTAL, ALTO + 150))
    pygame.display.set_caption("Agente en Laberinto Dinámico")
    clock = pygame.time.Clock()
    fuente = pygame.font.SysFont(None, 24)
    fuente_config = pygame.font.SysFont(None, 20)

    boton_reiniciar = pygame.Rect(ANCHO + 20, 380, 120, 30)
    boton_costo = pygame.Rect(ANCHO + 160, 380, 120, 30)
    texto_costo = "Costo: 0"
    boton_regresar_menu = pygame.Rect(ANCHO + 20, 420, 180, 30) 

    config_activa = True
    input_filas = pygame.Rect(ANCHO + 20, 50, 80, 25)
    input_columnas = pygame.Rect(ANCHO + 20, 90, 80, 25)
    texto_filas = str(FILAS_INICIAL)
    texto_columnas = str(COLUMNAS_INICIAL)
    color_activo = pygame.Color('lightskyblue3')
    color_inactivo = pygame.Color('grey')
    color_filas = color_inactivo
    color_columnas = color_inactivo
    activo_filas = False
    activo_columnas = False
    boton_generar = pygame.Rect(ANCHO + 20, 130, 150, 25)
    botones_tecnicas = {}
    tecnicas_disponibles_lista = ["BFS", "DFS", "Costo Uniforme", "Avara", "A*"]
    y_offset_tecnicas = 170
    for i, tecnica in enumerate(tecnicas_disponibles_lista):
        rect = pygame.Rect(ANCHO + 20, y_offset_tecnicas + i * 30, 180, 25)
        botones_tecnicas[tecnica] = (rect, True)
    boton_inicio = pygame.Rect(ANCHO + 20, y_offset_tecnicas + len(botones_tecnicas) * 30 + 20, 100, 25)
    boton_queso_huir = pygame.Rect(ANCHO + 20, boton_inicio.bottom + 15, 120, 25)
    boton_queso_aleatorio = pygame.Rect(ANCHO + 150, boton_inicio.bottom + 15, 120, 25)
    modo_queso_huida = True
    juego_iniciado = False

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if config_activa:
                    if input_filas.collidepoint(evento.pos):
                        activo_filas = True
                        activo_columnas = False
                    elif input_columnas.collidepoint(evento.pos):
                        activo_columnas = True
                        activo_filas = False
                    elif boton_generar.collidepoint(evento.pos):
                        try:
                            nuevas_filas = int(texto_filas)
                            nuevas_columnas = int(texto_columnas)
                            if nuevas_filas > 0 and nuevas_columnas > 0:
                                FILAS = nuevas_filas
                                COLUMNAS = nuevas_columnas
                                matriz_configuracion = generar_matriz_inicial(FILAS, COLUMNAS)
                                matriz, pos_agente, metodo_actual, llego_queso, costo_total_agente = resetear_juego(FILAS, COLUMNAS, matriz_configuracion, tecnicas_seleccionadas)
                                print(f"Laberinto redimensionado a {FILAS}x{COLUMNAS}")
                        except ValueError:
                            print("Por favor, introduce números válidos para filas y columnas.")
                    elif boton_inicio.collidepoint(evento.pos):
                        config_activa = False
                        juego_iniciado = True
                        tecnicas_seleccionadas = [tecnica for tecnica, (rect, seleccionado) in botones_tecnicas.items() if seleccionado]
                        if not tecnicas_seleccionadas:
                            tecnicas_seleccionadas = ["A*"]
                        matriz, pos_agente, metodo_actual, llego_queso, costo_total_agente = resetear_juego(FILAS, COLUMNAS, matriz_configuracion, tecnicas_seleccionadas)
                    elif boton_queso_huir.collidepoint(evento.pos):
                        modo_queso_huida = True
                    elif boton_queso_aleatorio.collidepoint(evento.pos):
                        modo_queso_huida = False
                    else:
                        for tecnica, (rect, seleccionado) in botones_tecnicas.items():
                            if rect.collidepoint(evento.pos):
                                botones_tecnicas[tecnica] = (rect, not seleccionado)
                                break
                elif juego_iniciado:
                    if boton_reiniciar.collidepoint(evento.pos):
                        matriz, pos_agente, metodo_actual, llego_queso, costo_total_agente = resetear_juego(FILAS, COLUMNAS, matriz_configuracion, tecnicas_seleccionadas)
                        costo_total_agente = 0
                        print("Juego reiniciado.")
                    elif boton_costo.collidepoint(evento.pos):
                        print(f"Costo total del agente: {costo_total_agente}")
                    elif boton_regresar_menu.collidepoint(evento.pos):
                        config_activa = True
                        juego_iniciado = False
                        print("Regresando al menú.")
            if evento.type == pygame.KEYDOWN:
                if config_activa:
                    if activo_filas:
                        if evento.key == pygame.K_RETURN:
                            activo_filas = False
                            color_filas = color_inactivo
                        elif evento.key == pygame.K_BACKSPACE:
                            texto_filas = texto_filas[:-1]
                        else:
                            texto_filas += evento.unicode
                    elif activo_columnas:
                        if evento.key == pygame.K_RETURN:
                            activo_columnas = False
                            color_columnas = color_inactivo
                        elif evento.key == pygame.K_BACKSPACE:
                            texto_columnas = texto_columnas[:-1]
                        else:
                            texto_columnas += evento.unicode

        ventana.fill(GRIS)

        if config_activa:
            """texto_filas_label = fuente_config.render("Filas:", True, NEGRO)
            ventana.blit(texto_filas_label, (ANCHO + 20, 30))
            pygame.draw.rect(ventana, color_filas, input_filas, 2)
            texto_superficie_filas = fuente_config.render(texto_filas, True, NEGRO)
            ventana.blit(texto_superficie_filas, (input_filas.x + 5, input_filas.y + 5))

            texto_columnas_label = fuente_config.render("Columnas:", True, NEGRO)
            ventana.blit(texto_columnas_label, (ANCHO + 20, 70))
            pygame.draw.rect(ventana, color_columnas, input_columnas, 2)
            texto_superficie_columnas = fuente_config.render(texto_columnas, True, NEGRO)
            ventana.blit(texto_superficie_columnas, (input_columnas.x + 5, input_columnas.y + 5))

            pygame.draw.rect(ventana, (100, 100, 100), boton_generar)
            texto_generar = fuente_config.render("Generar Laberinto", True, BLANCO)
            texto_rect_generar = texto_generar.get_rect(center=boton_generar.center)
            ventana.blit(texto_generar, texto_rect_generar)"""

            texto_tecnicas_label = fuente_config.render("Técnicas de Búsqueda:", True, NEGRO)
            ventana.blit(texto_tecnicas_label, (ANCHO + 20, 150))
            for tecnica, (rect, seleccionado) in botones_tecnicas.items():
                color_boton = VERDE if seleccionado else ROJO
                pygame.draw.rect(ventana, color_boton, rect)
                texto_boton = fuente_config.render(tecnica, True, BLANCO)
                texto_rect_boton = texto_boton.get_rect(center=rect.center)
                ventana.blit(texto_boton, texto_rect_boton)

            pygame.draw.rect(ventana, (50, 150, 50), boton_inicio)
            texto_inicio = fuente_config.render("Iniciar Juego", True, BLANCO)
            texto_rect_inicio = texto_inicio.get_rect(center=boton_inicio.center)
            ventana.blit(texto_inicio, texto_rect_inicio)

            color_huir = AZUL if modo_queso_huida else GRIS
            pygame.draw.rect(ventana, color_huir, boton_queso_huir)
            texto_huir = fuente_config.render("Queso Huye", True, BLANCO)
            texto_rect_huir = texto_huir.get_rect(center=boton_queso_huir.center)
            ventana.blit(texto_huir, texto_rect_huir)

            color_aleatorio = AZUL if not modo_queso_huida else GRIS
            pygame.draw.rect(ventana, color_aleatorio, boton_queso_aleatorio)
            texto_aleatorio = fuente_config.render("Queso Aleatorio", True, BLANCO)
            texto_rect_aleatorio = texto_aleatorio.get_rect(center=boton_queso_aleatorio.center)
            ventana.blit(texto_aleatorio, texto_rect_aleatorio)

        elif juego_iniciado:
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

            pygame.draw.circle(ventana, ROJO, (pos_agente[1] * TAM_CELDA + TAM_CELDA // 2, pos_agente[0] * TAM_CELDA + TAM_CELDA // 2), TAM_CELDA // 4)

            ventana_arbol = pygame.Surface((ANCHO, 150))
            ventana_arbol.fill(BLANCO)
            pygame.draw.rect(ventana_arbol, NEGRO, pygame.Rect(0, 0, ANCHO, 150), 2)
            if camino:
                dibujar_arbol(grafo, camino, ventana_arbol)
            ventana.blit(ventana_arbol, (0, ALTO))

            texto_tecnica = fuente.render(f"Técnica: {metodo_actual}", True, (0, 0, 0))
            ventana.blit(texto_tecnica, (ANCHO + 20, 350 - 30)) # Ajuste para el botón de reiniciar

            pygame.draw.rect(ventana, (100, 100, 100), boton_reiniciar)
            texto_reiniciar = fuente.render("Reiniciar", True, BLANCO)
            texto_rect_reiniciar = texto_reiniciar.get_rect(center=boton_reiniciar.center)
            ventana.blit(texto_reiniciar, texto_rect_reiniciar)

            pygame.draw.rect(ventana, (80, 80, 80), boton_costo)
            texto_costo_render = fuente.render(texto_costo, True, BLANCO)
            texto_rect_costo = texto_costo_render.get_rect(center=boton_costo.center)
            ventana.blit(texto_costo_render, texto_rect_costo)

            pygame.draw.rect(ventana, (150, 50, 50), boton_regresar_menu)
            texto_regresar = fuente.render("Regresar al Menú", True, BLANCO)
            texto_rect_regresar = texto_regresar.get_rect(center=boton_regresar_menu.center)
            ventana.blit(texto_regresar, texto_rect_regresar)

            if not llego_queso:
                grafo = crear_grafo_desde_matriz(matriz)
                objetivo = encontrar_queso(matriz)
                if objetivo:
                    camino, arbol = buscar_camino(metodo_actual, matriz, pos_agente, objetivo)
                    print(f"La función buscar_camino devolvió: (camino={camino}, arbol={arbol}) con la técnica: {metodo_actual}")
                    if camino and len(camino) > 1:
                        siguiente_pos = camino[1]
                        costo_movimiento = 1
                        if matriz[siguiente_pos[0]][siguiente_pos[1]] == 2:
                            costo_movimiento = 5
                        costo_total_agente += costo_movimiento
                        texto_costo = f"Costo: {costo_total_agente}"
                        matriz[pos_agente[0]][pos_agente[1]] = 0
                        pos_agente = siguiente_pos
                        matriz[pos_agente[0]][pos_agente[1]] = 4
                    elif pos_agente == objetivo:
                        llego_queso = True
                        print("¡El agente encontró el queso!")
                    else:
                        print(f"No se encontró un camino con {metodo_actual}. Cambiando de técnica...")
                        if len(tecnicas_seleccionadas) > 1:
                            indice_actual = tecnicas_seleccionadas.index(metodo_actual)
                            indice_siguiente = (indice_actual + 1) % len(tecnicas_seleccionadas)
                            metodo_actual = tecnicas_seleccionadas[indice_siguiente]
                            print(f"Nueva técnica: {metodo_actual}")
                        else:
                            print("No hay más técnicas para probar.")
                else:
                    print("El queso ha desaparecido.")

                if not llego_queso:
                    if modo_queso_huida:
                        matriz = mover_queso_huir(pos_agente, matriz)
                    else:
                        matriz = mover_queso_aleatorio(matriz)
                    matriz = mover_enemigos(pos_agente, matriz, metodo_actual)
                    if random.randint(0, 100) < 60: # Mover pared con un 10% de probabilidad
                        matriz = mover_pared_aleatorio(matriz)

        pygame.display.flip()
        clock.tick(5)

if __name__ == '__main__':
    iniciar_simulacion()