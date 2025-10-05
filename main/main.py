# main.py
import random
from funciones import crear_tablero, colocar_barcos, print_tablero, parse_coord, disparar

def jugar_terminal(auto_colocar_player: bool = True):
    tamaño = 10
    player = crear_tablero(tamaño)
    cpu = crear_tablero(tamaño)
    colocar_barcos(player)
    colocar_barcos(cpu)
    tiros_jugador = set()
    tiros_cpu = set()
    
    while True:
        print("\nTu turno. Tablero enemigo (oculto):")