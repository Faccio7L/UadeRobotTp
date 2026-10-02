import os
import json
import re


def cargar_todos_los_mapas(carpeta):
    mapas = {}

    for archivo in os.listdir(carpeta):
        if archivo.startswith("mapa") and archivo.endswith(".json"):
            numero = int(archivo[4:-5]) #desde 4 hasta -5. Osea omitiendo "mapa" y "json". Solo queda el num.

            with open(os.path.join(carpeta, archivo), "r", encoding="utf-8") as arch:
                mapas[numero] = json.load(arch)

    return mapas, len(mapas)






def main():
    mapas, cantidad_mapas = cargar_todos_los_mapas("mapas") 

    while True:
        try:
            mapa = int(input(f"Hay {cantidad_mapas} mapas disponibles.Ingrese el numero del mapa: "
            ))
            if mapa not in mapas:
                print("Por favor elija un mapa válido.")
            else:
                print(f"Mapa {mapa} cargado exitosamente.")
                seleccionado = mapas[mapa]
                break

        except ValueError:
            print("Por favor ingrese un número válido.")
    algoritmo_greedy(seleccionado)






def algoritmo_greedy(mapa):
    posiciones_visitas = set() #para no repetir posiciones
    inicio = tuple(mapa["inicio"]) # Convertido a tupla para que sea compatible con set
    fin = tuple(mapa["destino"])
    tamanio = mapa["tamano_celda_metros"]
    orientacion = mapa["orientacion_inicial"]
    maxPasos = mapa["maximo_pasos"]
    posicion = inicio #valor inicial inicio
    pasos = 0
    grilla = mapa["grilla"]
    posiciones_visitas.add(posicion)

    while pasos < maxPasos:
        if posicion == fin:
            print(f"¡El robot llegó al destino. Llego en {pasos} pasos.")
            break

        M_derecha, M_izquierda, M_arriba, M_abajo = encontrarMejorManhattan(posicion,fin,grilla,posiciones_visitas)

        Manhattan_optimo = min(M_derecha, M_izquierda, M_abajo, M_arriba)
        if Manhattan_optimo == float("inf"):
            print("No hay movimientos posibles")
            break
    #ACA ESTA EL ORDEN DE PRIORIDAD DE MOVIMIENTO! EN CASO DE EMPATE DER,IZQ,ABAJO,ARRIBA
        if Manhattan_optimo == M_derecha: 
            posicion = Mover_Robot("derecha",posicion)
        elif Manhattan_optimo == M_izquierda:
            posicion = Mover_Robot("izquierda",posicion)
        elif Manhattan_optimo == M_abajo:
            posicion = Mover_Robot("abajo",posicion)
        elif Manhattan_optimo == M_arriba:
            posicion = Mover_Robot("arriba",posicion)
        pasos += 1
        posiciones_visitas.add(posicion)
    if pasos >= maxPasos:
        print("Se alcanzó el máximo de pasos permitidos. El robot no llegó al destino.")





def encontrarMejorManhattan(posicion,fin,grilla,posiciones_visitas):
    if posicion[1] + 1 >= len(grilla[0]) or grilla[posicion[0]][posicion[1]+1] in (1, 2) or (posicion[0], posicion[1]+1) in posiciones_visitas: 
            M_derecha = float("inf")
    else:
            M_derecha= Manhattan((posicion[0],posicion[1]+1),fin)

    if posicion[1] - 1 < 0 or grilla[posicion[0]][posicion[1]-1] in (1, 2) or (posicion[0], posicion[1]-1) in posiciones_visitas: 
            M_izquierda = float("inf")
    else:
            M_izquierda = Manhattan((posicion[0],posicion[1]-1),fin)

    if posicion[0] - 1 < 0 or grilla[posicion[0]-1][posicion[1]] in (1, 2) or (posicion[0]-1, posicion[1]) in posiciones_visitas: 
            M_arriba = float("inf")
    else:
            M_arriba = Manhattan((posicion[0]-1,posicion[1]),fin)

    if posicion[0] + 1 >= len(grilla) or grilla[posicion[0]+1][posicion[1]] in (1, 2) or (posicion[0]+1, posicion[1]) in posiciones_visitas: 
            M_abajo = float("inf")
    else:
            M_abajo = Manhattan((posicion[0]+1,posicion[1]),fin)    
    return M_derecha, M_izquierda, M_arriba, M_abajo
    
    




def Mover_Robot(direccion,posicion):
    if direccion == "derecha":
        posicion = (posicion[0],posicion[1]+1)
    elif direccion == "izquierda":
        posicion = (posicion[0],posicion[1]-1)
    elif direccion == "abajo":
        posicion = (posicion[0]+1,posicion[1])
    elif direccion == "arriba":
        posicion = (posicion[0]-1,posicion[1])
    print(f"El robot se movió hacia {direccion}. Nueva posición: {posicion}")
    return posicion
        






def Manhattan(inicio,fin):
    return abs(inicio[0]-fin[0]) + abs(inicio[1]-fin[1])
    #[0] hace referencia a columna, [1] hace referencia a fila.

main()