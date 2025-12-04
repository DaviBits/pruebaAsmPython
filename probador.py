from cffi import FFI
import _game_lib

lib = _game_lib.lib

lib.init_rand_seed()

print("=== PRUEBA rnd(max) ===")
print("rnd(10) ->", lib.rnd(6))

print("\n=== PRUEBA lenCad ===")
cad = b"hola mundo"
tam = lib.lenCad(cad)
print(f"lenCad('hola mundo') = {tam}")

print("\n=== PRUEBA cmpCad ===")
c1 = b"perro"
c2 = b"perro"
c3 = b"gato"

print("cmpCad(perro, perro) =", lib.cmpCad(c1, c2))
print("cmpCad(perro, gato)  =", lib.cmpCad(c1, c3))

print("\n=== PRUEBA charInCad ===")
print("charInCad('a', 'perro') =", lib.charInCad(b'a', b"perro"))
print("charInCad('r', 'perro') =", lib.charInCad(b'r', b"perro"))

print("\n=== PRUEBA mezclarCadena ===")

ffi = FFI()
buffer = ffi.new("char[]", b"abcdef")

print("Antes:", ffi.string(buffer).decode())
lib.mezclarCadena(buffer)
print("Después:", ffi.string(buffer).decode())

# Nuevas funciones añadidas

def letraEnPosicion(letra, palabra, posicion):
    if posicion < 0 or posicion >= len(palabra):
        return 0
    return 1 if palabra[posicion] == letra else 0

def contarOcurrencias(letra, palabra):
    return palabra.count(letra)

def obtenerPista(palabra, palabraOculta):
    if not palabraOculta:
        return palabraOculta
    
    resultado = list(palabraOculta)
    ocultas = [i for i, c in enumerate(palabraOculta) if c == '_']
    
    if ocultas:
        pos = lib.rnd(len(ocultas) - 1)
        resultado[ocultas[pos]] = palabra[ocultas[pos]]
    
    return ''.join(resultado)

def cmpCadIgnoreCase(cad1, cad2):
    return cad1.lower() == cad2.lower()

def letrasUnicas(palabra):
    unicas = set(palabra.upper())
    letras_ordenadas = sorted([c for c in unicas if 'A' <= c <= 'Z'])
    return ''.join(letras_ordenadas)

# Pruebas de las nuevas funciones
print("\n=== PRUEBA letraEnPosicion ===")
print("letraEnPosicion('h', 'hola', 0) =", letraEnPosicion('h', "hola", 0))
print("letraEnPosicion('h', 'hola', 2) =", letraEnPosicion('h', "hola", 2))

print("\n=== PRUEBA contarOcurrencias ===")
print("contarOcurrencias('a', 'banana') =", contarOcurrencias('a', "banana"))
print("contarOcurrencias('n', 'banana') =", contarOcurrencias('n', "banana"))

print("\n=== PRUEBA obtenerPista ===")
print("obtenerPista('python', 'p__ho_') ->", obtenerPista("python", "p__ho_"))
print("obtenerPista('python', '______') ->", obtenerPista("python", "______"))

print("\n=== PRUEBA cmpCadIgnoreCase ===")
print("cmpCadIgnoreCase('Hola', 'HOLA') =", cmpCadIgnoreCase("Hola", "HOLA"))
print("cmpCadIgnoreCase('Hola', 'Mundo') =", cmpCadIgnoreCase("Hola", "Mundo"))

print("\n=== PRUEBA letrasUnicas ===")
print("letrasUnicas('programacion') =", letrasUnicas("programacion"))
print("letrasUnicas('banana') =", letrasUnicas("banana"))
from cffi import FFI
import _game_lib

lib = _game_lib.lib

lib.init_rand_seed()

print("=== PRUEBA rnd(max) ===")
print("rnd(10) ->", lib.rnd(6))

print("\n=== PRUEBA lenCad ===")
cad = b"hola mundo"
tam = lib.lenCad(cad)
print(f"lenCad('hola mundo') = {tam}")

print("\n=== PRUEBA cmpCad ===")
c1 = b"perro"
c2 = b"perro"
c3 = b"gato"

print("cmpCad(perro, perro) =", lib.cmpCad(c1, c2))
print("cmpCad(perro, gato)  =", lib.cmpCad(c1, c3))

print("\n=== PRUEBA charInCad ===")
print("charInCad('a', 'perro') =", lib.charInCad(b'a', b"perro"))
print("charInCad('r', 'perro') =", lib.charInCad(b'r', b"perro"))

print("\n=== PRUEBA mezclarCadena ===")

ffi = FFI()
buffer = ffi.new("char[]", b"abcdef")

print("Antes:", ffi.string(buffer).decode())
lib.mezclarCadena(buffer)
print("Después:", ffi.string(buffer).decode())

# Nuevas funciones añadidas

def letraEnPosicion(letra, palabra, posicion):
    if posicion < 0 or posicion >= len(palabra):
        return 0
    return 1 if palabra[posicion] == letra else 0

def contarOcurrencias(letra, palabra):
    return palabra.count(letra)

def obtenerPista(palabra, palabraOculta):
    if not palabraOculta:
        return palabraOculta
    
    resultado = list(palabraOculta)
    ocultas = [i for i, c in enumerate(palabraOculta) if c == '_']
    
    if ocultas:
        pos = lib.rnd(len(ocultas) - 1)
        resultado[ocultas[pos]] = palabra[ocultas[pos]]
    
    return ''.join(resultado)

def cmpCadIgnoreCase(cad1, cad2):
    return cad1.lower() == cad2.lower()

def letrasUnicas(palabra):
    unicas = set(palabra.upper())
    letras_ordenadas = sorted([c for c in unicas if 'A' <= c <= 'Z'])
    return ''.join(letras_ordenadas)

# Pruebas de las nuevas funciones
print("\n=== PRUEBA letraEnPosicion ===")
print("letraEnPosicion('h', 'hola', 0) =", letraEnPosicion('h', "hola", 0))
print("letraEnPosicion('h', 'hola', 2) =", letraEnPosicion('h', "hola", 2))

print("\n=== PRUEBA contarOcurrencias ===")
print("contarOcurrencias('a', 'banana') =", contarOcurrencias('a', "banana"))
print("contarOcurrencias('n', 'banana') =", contarOcurrencias('n', "banana"))

print("\n=== PRUEBA obtenerPista ===")
print("obtenerPista('python', 'p__ho_') ->", obtenerPista("python", "p__ho_"))
print("obtenerPista('python', '______') ->", obtenerPista("python", "______"))

print("\n=== PRUEBA cmpCadIgnoreCase ===")
print("cmpCadIgnoreCase('Hola', 'HOLA') =", cmpCadIgnoreCase("Hola", "HOLA"))
print("cmpCadIgnoreCase('Hola', 'Mundo') =", cmpCadIgnoreCase("Hola", "Mundo"))

print("\n=== PRUEBA letrasUnicas ===")
print("letrasUnicas('programacion') =", letrasUnicas("programacion"))
print("letrasUnicas('banana') =", letrasUnicas("banana"))