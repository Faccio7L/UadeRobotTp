def main():
    while true:
        try:
            mapa = int(input("1. Mapa 1\n2. Mapa 2\n3. Mapa 3\nIngrese el número del mapa: "))
            break
        except Exception as e:
            print("Por favor elija un numero valido.")
    elegir_coordenadas(mapa)

def elegir_coordenadas(mapa):