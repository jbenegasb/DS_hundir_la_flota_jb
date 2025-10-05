
# %%
import numpy as np

def crear_tablero(tamaño: int=10) -> np.ndarray:
    """
    crea y devuelve un tablero tamaño x tamaño relleno de '_'.
    internamente se usan indices 0...tamaño -1
    """
    tablero = np.full((tamaño, tamaño), "_", dtype='<U1')
    return tablero

tablero = crear_tablero()
print(tablero)

# %%
#mostrar el tablero en la terminal con cabecera A B C... y filas numeradas ( 123...)

def print_tablero(tablero:np.ndarray, ocultar_barcos: bool = False) -> None:
    tamaño = tablero.shape[0] 
    #cabera ABC...
    letras = [chr(ord('A')+ i) for i in range(tamaño)] 
    print(" " + " ".join(letras))
    for i in range(tamaño):
        fila_mostrar = []
        for j in range(tamaño):
            val = tablero[i,j]
            if ocultar_barcos and val == '0':
                fila_mostrar.append("_")
            else:
                fila_mostrar.append(val)

    #imprimimos filas numeradas 1..N para que sea intuitivo
        print(f"{i+1:2} " + " ".join(fila_mostrar))
    

# %%
from typing import List, Tuple

def dentro_tablero(pos: Tuple[int,int], tamaño: int) -> bool:
    r, c= pos 
    return 0 <= r < tamaño and 0 <= c < tamaño

def colocar_barco(barco: List[Tuple[int,int]], tablero: np.ndarray) -> bool:
    tamaño = tablero.shape[0]
    #Validacion previa 
    for (r, c) in barco:
        if not dentro_tablero((r, c), tamaño):
            return False
        if tablero[r, c] != "_":
            return False
    
    #colocar
    for (r,c) in barco :
        tablero[r,c] = "0"
    return True

t = crear_tablero(5)
b1 = [(0,1),(1,1)]   # vertical de 2
b2 = [(1,3),(1,4),(1,5),(1,6)]  # en 5x5 se saldría: será False
print(colocar_barco(b1,t))  # True (si está libre)
print(colocar_barco(b2,t))  # False (fuera)

# %%
#disparar
def disparar (casilla:tuple [int,int], tablero: np.ndarray) -> str:
    r, c = casilla 
    tamaño = tablero.shape[0]
    if not dentro_tablero((r,c), tamaño):
        return 'fuera'
    val = tablero[r, c]
    if val == 'O':
        tablero[r, c] = 'X'
        return 'tocado'
    elif val == '_':
        tablero[r, c] = 'A'
        return 'agua'
    elif val in ('X', 'A'):
        return 'repetido'
    else:
        return 'otro'

# %%
# creacion de los barcos 

import random
from typing import Optional

def casillas_vecinas(pos: Tuple[int,int], tamaño: int) -> List[Tuple[int,int]]:
    """Devuelve todas las casillas adyacentes (8 direcciones) dentro del tablero."""
    r, c = pos
    vecinos = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < tamaño and 0 <= cc < tamaño:
                vecinos.append((rr, cc))
    return vecinos

def crear_barco(eslora: int, tamaño: int = 10, tablero: Optional[np.ndarray] = None,
                max_intentos: int = 1000, no_touch: bool = False) -> List[Tuple[int,int]]:
    direcciones = ['N', 'S', 'E', 'W']
    intentos = 0
    while intentos < max_intentos:
        intentos += 1
        orient = random.choice(direcciones)
        r0 = random.randrange(0, tamaño)
        c0 = random.randrange(0, tamaño)
        coords = []
        for i in range(eslora):
            if orient == 'N':
                coords.append((r0 - i, c0))
            elif orient == 'S':
                coords.append((r0 + i, c0))
            elif orient == 'E':
                coords.append((r0, c0 + i))
            elif orient == 'W':
                coords.append((r0, c0 - i))
        # comprobar dentro del tablero
        if not all(dentro_tablero(pos, tamaño) for pos in coords):
            continue
        # comprobar casillas libres si se pasa tablero
        if tablero is not None:
            if any(tablero[r, c] != '_' for (r, c) in coords):
                continue
            if no_touch:
                # comprobar vecinos de cada casilla propuesta
                for (r, c) in coords:
                    for (rr, cc) in casillas_vecinas((r, c), tamaño):
                        if tablero[rr, cc] == 'O':
                            break
                    else:
                        continue
                    # rompimos porque encontramos vecino ocupado
                    break
                else:
                    # si no hemos roto, coords válidas
                    return coords
                # si rompimos, continuar intentos
                continue
        else:
            # Si no hay tablero dado y no_touch solicitado, no hay forma de comprobar, así que aceptamos coords
            pass
        # Si llegamos aquí y no_touch no activado, coords válidas
        return coords
    return []


# %%
def colocar_barcos(tablero: np.ndarray, flota: Optional[List[int]] = None,
                   no_touch: bool = False, max_intentos_por_barco: int = 300,
                   max_restarts: int = 50) -> List[List[Tuple[int,int]]]:
    if flota is None:
        flota = [2,2,2,3,3,4]
    tamaño = tablero.shape[0]
    restart_count = 0
    while restart_count < max_restarts:
        restart_count += 1
        tablero[:, :] = '_'  # limpiar
        barcos = []
        ok = True
        for eslora in flota:
            placed = False
            for _ in range(max_intentos_por_barco):
                coords = crear_barco(eslora, tamaño=tamaño, tablero=tablero, no_touch=no_touch)
                if not coords:
                    continue
                if colocar_barco(coords, tablero):
                    barcos.append(coords)
                    placed = True
                    break
            if not placed:
                ok = False
                break
        if ok:
            return barcos
    # Si llegamos aquí, no hemos podido colocar la flota
    raise RuntimeError("No se pudo colocar la flota tras varios intentos. Reduce restricciones o revisa el algoritmo.")

# %%
from typing import Optional

def parse_coord(s: str, tamaño: int = 10) -> Optional[Tuple[int,int]]:
    s = s.strip()
    if not s:
        return None
    # formato letra+numero: ex A5
    if len(s) >= 2 and s[0].isalpha():
        letter = s[0].upper()
        col = ord(letter) - ord('A')
        rest = s[1:].strip()
        if rest.isdigit():
            row = int(rest) - 1  # usuario usa 1..N
            if 0 <= row < tamaño and 0 <= col < tamaño:
                return (row, col)
            else:
                return None
    # formato 'fila,col' o 'fila col' -> asumimos 0-index
    for sep in (',', ' '):
        if sep in s:
            parts = [p for p in s.split(sep) if p != '']
            if len(parts) == 2 and parts[0].lstrip('-').isdigit() and parts[1].lstrip('-').isdigit():
                r = int(parts[0])
                c = int(parts[1])
                if 0 <= r < tamaño and 0 <= c < tamaño:
                    return (r, c)
                else:
                    return None
    return None


