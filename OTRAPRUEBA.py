import ctypes

# Carga la DLL
dll = ctypes.WinDLL("C:\\Users\\HP\\Desktop\\pruebaAsm\\prueba.dll")

# Definir la función Sumar
# int Sumar(int a, int b)
dll.Sumar.argtypes = [ctypes.c_int, ctypes.c_int]
dll.Sumar.restype = ctypes.c_int

# Probar
a = 5
b = 7
resultado = dll.Sumar(a, b)
print(f"{a} + {b} = {resultado}")
