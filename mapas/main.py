import os
import sys
import json

# Permite encontrar la API del robot G1 del simulador
_ruta_sim = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "04Simuladores", "UnitreeMujocoOficial"))
if _ruta_sim not in sys.path:
    sys.path.insert(0, _ruta_sim)

try:
    from g1_student_api import RobotG1
except ImportError:
    RobotG1 = None




def Manhattan(inicio, fin):
    """
    Calcula la distancia entre un punto de partida hasta un destino en una matriz
    Retorna la distancia.
    """
    return abs(inicio[0]-fin[0]) + abs(inicio[1]-fin[1])


def encontrarMejorManhattan(posicion, fin, grilla, posiciones_visitas):
    """
    Calcula Manhattan hacia norte,sur,este y oeste desde un punto inicial. Si se termina el mapa, se recorrio o
    hay un obstaculo, se retorna "infinito".
    """
    if posicion[1] + 1 >= len(grilla[0]) or grilla[posicion[0]][posicion[1]+1] in (1, 2) or (posicion[0], posicion[1]+1) in posiciones_visitas: 
        M_derecha = float("inf")
    else:
        M_derecha = Manhattan((posicion[0], posicion[1]+1), fin)

    if posicion[1] - 1 < 0 or grilla[posicion[0]][posicion[1]-1] in (1, 2) or (posicion[0], posicion[1]-1) in posiciones_visitas: 
        M_izquierda = float("inf")
    else:
        M_izquierda = Manhattan((posicion[0], posicion[1]-1), fin)

    if posicion[0] - 1 < 0 or grilla[posicion[0]][posicion[1]] in (1, 2) or (posicion[0]-1, posicion[1]) in posiciones_visitas: 
        M_arriba = float("inf")
    else:
        M_arriba = Manhattan((posicion[0]-1, posicion[1]), fin)

    if posicion[0] + 1 >= len(grilla) or grilla[posicion[0]+1][posicion[1]] in (1, 2) or (posicion[0]+1, posicion[1]) in posiciones_visitas: 
        M_abajo = float("inf")
    else:
        M_abajo = Manhattan((posicion[0]+1, posicion[1]), fin)    
    return M_derecha, M_izquierda, M_arriba, M_abajo
    

def nueva_ubicacion(direccion, posicion):
    """
    Calcula la próxima coordenada lógica en la grilla antes del movimiento físico.
    """
    if direccion == "derecha":
        posicion = (posicion[0], posicion[1]+1)
    elif direccion == "izquierda":
        posicion = (posicion[0], posicion[1]-1)
    elif direccion == "abajo":
        posicion = (posicion[0]+1, posicion[1])
    elif direccion == "arriba":
        posicion = (posicion[0]-1, posicion[1])
    print(f"El robot se desplazará hacia {direccion}. Próxima posición: {posicion}")
    return posicion


def generar_instrucciones(ruta, orientacion, tamanio):
    
    ori = orientacion.upper()
    pasos = []
    
    # Giros posibles segun donde miro y el cambio en (fila, columna)
    giros = {
        ("NORTE", 0, 1): "GIRAR DERECHA 90°", ("NORTE", 0, -1): "GIRAR IZQUIERDA 90°", ("NORTE", 1, 0): "GIRAR 180°",
        ("ESTE", 1, 0): "GIRAR DERECHA 90°", ("ESTE", -1, 0): "GIRAR IZQUIERDA 90°", ("ESTE", 0, -1): "GIRAR 180°",
        ("SUR", 0, -1): "GIRAR DERECHA 90°", ("SUR", 0, 1): "GIRAR IZQUIERDA 90°", ("SUR", -1, 0): "GIRAR 180°",
        ("OESTE", -1, 0): "GIRAR DERECHA 90°", ("OESTE", 1, 0): "GIRAR IZQUIERDA 90°", ("OESTE", 0, 1): "GIRAR 180°",
    }
    
    for i in range(len(ruta) - 1):
        
        (f1, c1) = ruta[i]
        (f2, c2) = ruta[i+1]
        
        df = f2 - f1
        dc = c2 - c1
        
        if df > 0: 
            destino = "SUR"
        elif dc > 0: 
            destino = "ESTE"
        elif dc < 0: 
            destino = "OESTE"
        else:
            destino = "NORTE"
        
        # Buscamos en el diccionario si hay que girar
        giro_texto = giros.get((ori, df, dc), "")
        if giro_texto:
            pasos.append(giro_texto)
            
        pasos.append(f"AVANZAR {tamanio} m")
        ori = destino
        
    return ", ".join(pasos)


def ejecutar_en_robot(robot, instrucciones):
    """
    Envía secuencialmente cada orden planificada de manera anterior. Estan todas las instrucciones planificadas.
"""
    TIEMPO_AVANCE = 2
    TIEMPO_GIRO = 3.14
    for paso in instrucciones.split(", "):
        paso = paso.strip()
        if "AVANZAR" in paso:
            robot.movimiento(adelante=0.25, tiempo=TIEMPO_AVANCE)
        elif "DERECHA" in paso:
            robot.movimiento(giro=-0.5, tiempo=TIEMPO_GIRO)
        elif "IZQUIERDA" in paso:
            robot.movimiento(giro=0.5, tiempo=TIEMPO_GIRO)
        elif "180" in paso:
            robot.movimiento(giro=0.5, tiempo=TIEMPO_GIRO * 2)


def algoritmo_greedy(mapa, robot=None):
    """
    Desarma el diccionario del mapa, se itera hasta encontrar(o no) la solucion.
    """
    posiciones_visitas = set()
    inicio = tuple(mapa["inicio"]) 
    fin = tuple(mapa["destino"])
    tamanio = mapa["tamano_celda_metros"]
    orientacion = mapa["orientacion_inicial"]
    maxPasos = mapa["maximo_pasos"]
    posicion = inicio
    pasos = 0
    grilla = mapa["grilla"]
    posiciones_visitas.add(posicion)
    
    ruta = [posicion] #lista de tuplas, contiene todas las posiciones visitadas en orden.

    while pasos < maxPasos:
        if posicion == fin:
            print(f"El robot llego en {pasos} pasos.")
            break

        M_derecha, M_izquierda, M_arriba, M_abajo = encontrarMejorManhattan(posicion, fin, grilla, posiciones_visitas)

        Manhattan_optimo = min(M_derecha, M_izquierda, M_abajo, M_arriba)
        if Manhattan_optimo == float("inf"):
            print("No hay movimientos posibles")
            break

        if Manhattan_optimo == M_derecha: 
            posicion = nueva_ubicacion("derecha", posicion)
        elif Manhattan_optimo == M_izquierda:
            posicion = nueva_ubicacion("izquierda", posicion)
        elif Manhattan_optimo == M_abajo:
            posicion = nueva_ubicacion("abajo", posicion)
        elif Manhattan_optimo == M_arriba:
            posicion = nueva_ubicacion("arriba", posicion)

        pasos += 1
        posiciones_visitas.add(posicion)
        ruta.append(posicion)
        
    if pasos >= maxPasos and posicion != fin:
        print("Se alcanzó el máximo de pasos permitidos. El robot no llegó al destino.")

    
    instrucciones = generar_instrucciones(ruta, orientacion, tamanio)
    print(instrucciones)

    if robot:
        ejecutar_en_robot(robot, instrucciones)


def cargar_todos_los_mapas(carpeta):
    """
    Importa todos los mapas.
    """
    mapas = {}

    for archivo in os.listdir(carpeta):
        if archivo.startswith("mapa") and archivo.endswith(".json"):
            numero = int(archivo[4:-5])

            with open(os.path.join(carpeta, archivo), "r", encoding="utf-8") as arch:
                mapas[numero] = json.load(arch)

    return mapas, len(mapas)


def main():
    """
    Hace que el usuario elija un mapa y despues se trabaja desde algoritmo_greedy.
    """
    mapas, cantidad_mapas = cargar_todos_los_mapas("mapas") 

    while True:
        try:
            mapa = int(input(f"Hay {cantidad_mapas} mapas disponibles.Ingrese el numero del mapa: "))
            if mapa not in mapas:
                print("Por favor elija un mapa válido.")
            else:
                print(f"Mapa {mapa} cargado exitosamente.")
                seleccionado = mapas[mapa]
                break

        except ValueError:
            print("Por favor ingrese un número válido.")

    robot = None
    if RobotG1 is not None:
        try:
            robot = RobotG1()
            robot.conectar()
        except Exception:
            print("El algoritmo se ejecutará en la consola.")
            robot = None

    try:
        algoritmo_greedy(seleccionado, robot)
    finally:
        if robot:
            robot.detenerse()
            robot.desconectar()


main()
