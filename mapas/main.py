import os
import sys
import json


_ruta_sim = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "04Simuladores", "UnitreeMujocoOficial"))
if _ruta_sim not in sys.path:
    sys.path.insert(0, _ruta_sim)

try:
    from g1_student_api import RobotG1
except ImportError:
    RobotG1 = None


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
    Calcula la proxima coordenada logica en la grilla antes del movimiento fisico.
    """
    if direccion == "derecha":
        posicion = (posicion[0], posicion[1]+1)
    elif direccion == "izquierda":
        posicion = (posicion[0], posicion[1]-1)
    elif direccion == "abajo":
        posicion = (posicion[0]+1, posicion[1])
    elif direccion == "arriba":
        posicion = (posicion[0]-1, posicion[1])
    print(f"El robot se desplazara hacia {direccion}. Proxima posicion: {posicion}")
    return posicion


def generar_instrucciones(ruta, orientacion, tamanio):
    """
    Genera la secuencia de giros y avances segun la ruta calculada.
    """
    orientacionNueva = orientacion.upper()
    pasos = []
       
    for i in range(len(ruta) - 1):
        (fila1, columna1) = ruta[i]
        (fila2, columna2) = ruta[i+1]
        
        df = fila2 - fila1
        dc = columna2 - columna1
        
        if df == 1: 
            destino = "SUR"
            if orientacionNueva == "ESTE": pasos.append("GIRAR DERECHA 90")
            elif orientacionNueva == "OESTE": pasos.append("GIRAR IZQUIERDA 90")
            elif orientacionNueva == "NORTE": pasos.append("GIRAR 180")
        elif dc == 1: 
            destino = "ESTE"
            if orientacionNueva == "NORTE": pasos.append("GIRAR DERECHA 90")
            elif orientacionNueva == "SUR": pasos.append("GIRAR IZQUIERDA 90")
            elif orientacionNueva == "OESTE": pasos.append("GIRAR 180")
        elif dc == -1: 
            destino = "OESTE"
            if orientacionNueva == "SUR": pasos.append("GIRAR DERECHA 90")
            elif orientacionNueva == "NORTE": pasos.append("GIRAR IZQUIERDA 90")
            elif orientacionNueva == "ESTE": pasos.append("GIRAR 180")
        else:
            destino = "NORTE"
            if orientacionNueva == "OESTE": pasos.append("GIRAR DERECHA 90")
            elif orientacionNueva == "ESTE": pasos.append("GIRAR IZQUIERDA 90")
            elif orientacionNueva == "SUR": pasos.append("GIRAR 180")
        
        pasos.append("AVANZAR") #si gira, se agrega el giro y dsp que camine medio metro.
        orientacionNueva = destino
        
    return pasos


def ejecutar_en_robot(robot, instrucciones):
    """
    Envia secuencialmente cada orden planificada de manera anterior.
    """
    TiempoAvance = 2
    TiempoGiro = 3.14
    for paso in instrucciones:
        if "AVANZAR" in paso:
            robot.movimiento(adelante=0.25, tiempo=TiempoAvance) #ESTO ES METROS Y SEGUNDOS.
        elif "DERECHA" in paso:
            robot.movimiento(giro=-0.5, tiempo=TiempoGiro) #rota 90 grados en 3.14 segundos(pi)
        elif "IZQUIERDA" in paso:
            robot.movimiento(giro=0.5, tiempo=TiempoGiro)
        elif "180" in paso:
            robot.movimiento(giro=0.5, tiempo=TiempoGiro * 2)


def algoritmo_greedy(mapa, robot):
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
    
    ruta = [posicion]

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
        print("Se alcanzo el maximo de pasos permitidos. El robot no llego al destino.")

    instrucciones = generar_instrucciones(ruta, orientacion, tamanio)
    print(", ".join(instrucciones)) #para mostrarlas en pantalla.

    if robot:
        ejecutar_en_robot(robot, instrucciones)


def main():
    """
    Hace que el usuario elija un mapa y despues se trabaja desde algoritmo_greedy.
    """
    mapas, cantidad_mapas = cargar_todos_los_mapas("mapas") 

    while True:
        try:
            mapa = int(input(f"Hay {cantidad_mapas} mapas disponibles. Ingrese el numero del mapa: "))
            if mapa not in mapas:
                print("Por favor elija un mapa valido.")
            else:
                print(f"Mapa {mapa} cargado exitosamente.")
                seleccionado = mapas[mapa]
                break

        except ValueError:
            print("Por favor ingrese un numero valido.")

    robot = None
    if RobotG1 is not None:
        try:
            robot = RobotG1()
            robot.conectar()
        except Exception:
            print("El algoritmo se ejecutara en la consola.")
            robot = None

    try:
        algoritmo_greedy(seleccionado, robot)
    finally:
        if robot:
            robot.detenerse()
            robot.desconectar()


main()
