import os
import json

# -------------------------------------------------------------
# 1. CARGA Y VALIDACIÓN DEL MAPA
# -------------------------------------------------------------
def cargar_todos_los_mapas(carpeta=None):
    if carpeta is None:
        # Detecta automáticamente la carpeta 'mapas' relativa al script
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(os.path.join(directorio_actual, "mapa1.json")):
            carpeta = directorio_actual
        else:
            carpeta = os.path.join(directorio_actual, "mapas")

    mapas = {}
    for archivo in os.listdir(carpeta):
        if archivo.startswith("mapa") and archivo.endswith(".json"):
            numero = int(archivo[4:-5])
            with open(os.path.join(carpeta, archivo), "r", encoding="utf-8") as arch:
                datos = json.load(arch)
                validar_mapa(datos)
                mapas[numero] = datos

    return mapas, len(mapas)


def validar_mapa(mapa):
    claves_obligatorias = [
        "nombre", "grilla", "inicio", "destino",
        "tamano_celda_metros", "orientacion_inicial", "maximo_pasos"
    ]
    for clave in claves_obligatorias:
        if clave not in mapa:
            raise ValueError(f"Falta el metadato obligatorio '{clave}' en el mapa.")


# -------------------------------------------------------------
# 2. SELECCIÓN GREEDY Y MOVIMIENTO (Tus métodos con el desempate corregido)
# -------------------------------------------------------------
def Manhattan(pos1, pos2):
    # pos1[0] es FILA, pos1[1] es COLUMNA
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def encontrarMejorManhattan(posicion, fin, grilla, posiciones_visitas):
    filas = len(grilla)
    columnas = len(grilla[0])

    # ARRIBA: fila - 1
    if posicion[0] - 1 < 0 or grilla[posicion[0]-1][posicion[1]] in (1, 2) or (posicion[0]-1, posicion[1]) in posiciones_visitas:
        M_arriba = float("inf")
    else:
        M_arriba = Manhattan((posicion[0]-1, posicion[1]), fin)

    # DERECHA: columna + 1
    if posicion[1] + 1 >= columnas or grilla[posicion[0]][posicion[1]+1] in (1, 2) or (posicion[0], posicion[1]+1) in posiciones_visitas:
        M_derecha = float("inf")
    else:
        M_derecha = Manhattan((posicion[0], posicion[1]+1), fin)

    # ABAJO: fila + 1
    if posicion[0] + 1 >= filas or grilla[posicion[0]+1][posicion[1]] in (1, 2) or (posicion[0]+1, posicion[1]) in posiciones_visitas:
        M_abajo = float("inf")
    else:
        M_abajo = Manhattan((posicion[0]+1, posicion[1]), fin)

    # IZQUIERDA: columna - 1
    if posicion[1] - 1 < 0 or grilla[posicion[0]][posicion[1]-1] in (1, 2) or (posicion[0], posicion[1]-1) in posiciones_visitas:
        M_izquierda = float("inf")
    else:
        M_izquierda = Manhattan((posicion[0], posicion[1]-1), fin)

    return M_arriba, M_derecha, M_abajo, M_izquierda


def Mover_Robot(direccion, posicion):
    if direccion == "arriba":
        posicion = (posicion[0] - 1, posicion[1])
    elif direccion == "derecha":
        posicion = (posicion[0], posicion[1] + 1)
    elif direccion == "abajo":
        posicion = (posicion[0] + 1, posicion[1])
    elif direccion == "izquierda":
        posicion = (posicion[0], posicion[1] - 1)
    return posicion


def algoritmo_greedy(mapa):
    inicio = tuple(mapa["inicio"])
    fin = tuple(mapa["destino"])
    grilla = mapa["grilla"]
    maxPasos = mapa["maximo_pasos"]
    tamanio = mapa["tamano_celda_metros"]
    orientacion_inicial = mapa["orientacion_inicial"]

    posicion = inicio
    posiciones_visitas = {posicion}
    ruta = [posicion]  # <-- Registro de la ruta recorrida
    pasos = 0
    resultado = "LIMITE_DE_PASOS"

    while pasos < maxPasos:
        if posicion == fin:
            resultado = "DESTINO_ALCANZADO"
            break

        M_arriba, M_derecha, M_abajo, M_izquierda = encontrarMejorManhattan(
            posicion, fin, grilla, posiciones_visitas
        )

        Manhattan_optimo = min(M_arriba, M_derecha, M_abajo, M_izquierda)

        if Manhattan_optimo == float("inf"):
            resultado = "BLOQUEADO"
            break

        # CRITERIO DE DESEMPATE DEL PDF: ARRIBA -> DERECHA -> ABAJO -> IZQUIERDA
        if Manhattan_optimo == M_arriba:
            posicion = Mover_Robot("arriba", posicion)
        elif Manhattan_optimo == M_derecha:
            posicion = Mover_Robot("derecha", posicion)
        elif Manhattan_optimo == M_abajo:
            posicion = Mover_Robot("abajo", posicion)
        elif Manhattan_optimo == M_izquierda:
            posicion = Mover_Robot("izquierda", posicion)

        pasos += 1
        posiciones_visitas.add(posicion)
        ruta.append(posicion)

    if posicion == fin:
        resultado = "DESTINO_ALCANZADO"

    # Reporte formal
    print("\n" + "="*50)
    print(f"RESULTADO: {resultado}")
    print(f"Cantidad de pasos: {pasos} (máximo permitido: {maxPasos})")
    print(f"Ruta recorrida: {' -> '.join(str(p) for p in ruta)}")
    print("="*50)

    # Instrucciones físicas para el robot
    instrucciones = traducir_a_instrucciones(ruta, orientacion_inicial, tamanio)
    print(f"\nInstrucciones para el robot:\n{instrucciones}")

    # Representación textual de la grilla
    print("\nRepresentación textual del mapa:")
    mostrar_grilla(grilla, ruta, inicio, fin)

    return resultado, ruta, pasos


# -------------------------------------------------------------
# 3. TRADUCCIÓN A INSTRUCCIONES FÍSICAS (Faltante requerido)
# -------------------------------------------------------------
def traducir_a_instrucciones(ruta, orientacion_inicial, tamano_celda):
    if len(ruta) <= 1:
        return "SIN MOVIMIENTOS"

    CARDINALES = ["NORTE", "ESTE", "SUR", "OESTE"]
    MOV_A_CARDINAL = {
        (-1, 0): "NORTE",  # Arriba
        (0, 1): "ESTE",    # Derecha
        (1, 0): "SUR",     # Abajo
        (0, -1): "OESTE"   # Izquierda
    }

    instrucciones = []
    orient_actual = orientacion_inicial.upper()
    tam_formateado = f"{tamano_celda:.2f}".replace(".", ",")

    for i in range(len(ruta) - 1):
        actual = ruta[i]
        siguiente = ruta[i + 1]
        delta = (siguiente[0] - actual[0], siguiente[1] - actual[1])
        card_sig = MOV_A_CARDINAL[delta]

        idx_act = CARDINALES.index(orient_actual)
        idx_sig = CARDINALES.index(card_sig)
        diff = (idx_sig - idx_act) % 4

        if diff == 1:
            instrucciones.append("GIRAR DERECHA 90°")
        elif diff == 2:
            instrucciones.append("GIRAR 180°")
        elif diff == 3:
            instrucciones.append("GIRAR IZQUIERDA 90°")

        orient_actual = card_sig
        instrucciones.append(f"AVANZAR {tam_formateado} m")

    return " -> ".join(instrucciones)


# -------------------------------------------------------------
# 4. REPRESENTACIÓN TEXTUAL (Entregable 3)
# -------------------------------------------------------------
def mostrar_grilla(grilla, ruta, inicio, fin):
    ruta_set = set(ruta)
    for f in range(len(grilla)):
        linea = []
        for c in range(len(grilla[0])):
            pos = (f, c)
            if pos == inicio:
                linea.append("I")
            elif pos == fin:
                linea.append("D")
            elif grilla[f][c] == 1:
                linea.append("█")  # Obstáculo
            elif grilla[f][c] == 2:
                linea.append("X")  # Zona prohibida
            elif pos in ruta_set:
                linea.append("·")  # Paso transitado
            else:
                linea.append("0")  # Libre no transitado
        print(" ".join(linea))


# -------------------------------------------------------------
# 5. MENÚ PRINCIPAL
# -------------------------------------------------------------
def main():
    mapas, cantidad_mapas = cargar_todos_los_mapas()

    while True:
        try:
            mapa = int(input(f"\nHay {cantidad_mapas} mapas disponibles. Ingrese el número del mapa (1-{cantidad_mapas}): "))
            if mapa not in mapas:
                print("Por favor elija un mapa válido.")
            else:
                print(f"--- Ejecutando {mapas[mapa]['nombre']} ---")
                algoritmo_greedy(mapas[mapa])
                break
        except ValueError:
            print("Por favor ingrese un número válido.")

if __name__ == "__main__":
    main()
