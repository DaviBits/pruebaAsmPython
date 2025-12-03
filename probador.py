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
