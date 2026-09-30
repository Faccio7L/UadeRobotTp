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
    inicio = mapa["inicio"]
    fin = mapa["destino"]
    tamanio = mapa["tamano_celda_metros"]
    orientacion = mapa["orientacion_inicial"]
    maxPasos = mapa["maximo_pasos"]
    
def Manhattan(inicio,fin):
    return abs(inicio[0]-fin[0]) + abs(inicio[1]-fin[1])
    #[0] hace referencia a columna, [1] hace referencia a fila.

main()

