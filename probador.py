from cffi import FFI
import _game_lib
import time

lib = _game_lib.lib
ffi = FFI()

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
buffer = ffi.new("char[]", b"abcdef")
print("Antes:", ffi.string(buffer).decode())
lib.mezclarCadena(buffer)
print("Después:", ffi.string(buffer).decode())

# ============================================
# PRUEBAS DE TEMPORIZADOR
# ============================================
print("\n" + "="*50)
print("PRUEBAS DE TEMPORIZADOR")
print("="*50)

# -----------------------------------------------------------------
# 1. Iniciar temporizador
# -----------------------------------------------------------------
print("\n1. Iniciando temporizador...")
lib.iniciar_temporizador()
print("   ✅ Temporizador iniciado")

# -----------------------------------------------------------------
# 2. Obtener tiempo actual mientras corre
# -----------------------------------------------------------------
print("\n2. Probando obtener_tiempo_actual():")
print("   Esperando 1 segundo...")
time.sleep(1)

tiempo_actual = lib.obtener_tiempo_actual()
print(f"   Tiempo actual: {tiempo_actual} ms")

# Formatear el tiempo
buffer_tiempo = ffi.new("char[]", 20)
lib.formato_tiempo_mm_ss(tiempo_actual, buffer_tiempo)
tiempo_formateado = ffi.string(buffer_tiempo).decode()
print(f"   Tiempo formateado: {tiempo_formateado}")

# -----------------------------------------------------------------
# 3. Esperar un poco más y verificar
# -----------------------------------------------------------------
print("\n3. Esperando 0.5 segundos más...")
time.sleep(0.5)

tiempo_actual2 = lib.obtener_tiempo_actual()
print(f"   Tiempo actual: {tiempo_actual2} ms")

lib.formato_tiempo_mm_ss(tiempo_actual2, buffer_tiempo)
tiempo_formateado2 = ffi.string(buffer_tiempo).decode()
print(f"   Tiempo formateado: {tiempo_formateado2}")

# -----------------------------------------------------------------
# 4. Detener temporizador
# -----------------------------------------------------------------
print("\n4. Deteniendo temporizador...")
tiempo_final = lib.detener_temporizador()
print(f"   Tiempo final: {tiempo_final} ms")

lib.formato_tiempo_mm_ss(tiempo_final, buffer_tiempo)
tiempo_formateado_final = ffi.string(buffer_tiempo).decode()
print(f"   Tiempo formateado final: {tiempo_formateado_final}")

# -----------------------------------------------------------------
# 5. Prueba: Temporizador múltiples veces
# -----------------------------------------------------------------
print("\n5. Prueba: Múltiples temporizadores rápidos:")
for i in range(3):
    lib.iniciar_temporizador()
    time.sleep(0.1 * (i + 1))  # 0.1s, 0.2s, 0.3s
    tiempo = lib.detener_temporizador()
    lib.formato_tiempo_mm_ss(tiempo, buffer_tiempo)
    tiempo_str = ffi.string(buffer_tiempo).decode()
    print(f"   Temporizador {i+1}: {tiempo} ms ({tiempo_str})")

# -----------------------------------------------------------------
# 6. Prueba: Tiempo exacto (comparación con Python)
# -----------------------------------------------------------------
print("\n6. Prueba de precisión (vs time.sleep):")
lib.iniciar_temporizador()

# Medir con Python también
inicio_python = time.time()
time.sleep(1.5)  # 1.5 segundos exactos
fin_python = time.time()

tiempo_c = lib.detener_temporizador()
tiempo_python = int((fin_python - inicio_python) * 1000)  # Convertir a ms

print(f"   Tiempo C/ASM: {tiempo_c} ms")
print(f"   Tiempo Python: {tiempo_python} ms")
print(f"   Diferencia: {abs(tiempo_c - tiempo_python)} ms")

if abs(tiempo_c - tiempo_python) < 50:  # Margen de error de 50ms
    print("   ✅ Precisión aceptable")
else:
    print("   ⚠️  Gran diferencia en tiempos")

# ============================================
# PRUEBAS DE OTRAS FUNCIONES (manteniendo las tuyas)
# ============================================
print("\n" + "="*50)
print("PRUEBAS DE OTRAS FUNCIONES")
print("="*50)

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

# ============================================
# PRUEBA ADICIONAL: Juego simulado con temporizador
# ============================================
print("\n" + "="*50)
print("SIMULACIÓN DE JUEGO CON TEMPORIZADOR")
print("="*50)

def simular_juego():
    print("\n🎮 Iniciando simulación de juego...")
    
    # 1. Iniciar temporizador del nivel
    lib.iniciar_temporizador()
    print("   ⏱️  Temporizador iniciado")
    
    # 2. Simular tiempo de pensamiento
    print("   🤔 Jugador pensando...")
    time.sleep(2.3)  # 2.3 segundos pensando
    
    # 3. Mostrar tiempo transcurrido
    tiempo_pensamiento = lib.obtener_tiempo_actual()
    buffer_temp = ffi.new("char[]", 20)
    lib.formato_tiempo_mm_ss(tiempo_pensamiento, buffer_temp)
    print(f"   ⏰ Tiempo pensando: {ffi.string(buffer_temp).decode()}")
    
    # 4. Simular que encontró la respuesta
    print("   💡 ¡Encontró la respuesta!")
    time.sleep(0.7)  # 0.7 segundos para escribir
    
    # 5. Completar nivel y obtener tiempo final
    tiempo_total = lib.detener_temporizador()
    lib.formato_tiempo_mm_ss(tiempo_total, buffer_temp)
    tiempo_final_str = ffi.string(buffer_temp).decode()
    
    print(f"   ✅ Nivel completado en: {tiempo_final_str} ({tiempo_total} ms)")
    
    # 6. Evaluar desempeño
    if tiempo_total < 2000:
        print("   🏆 ¡Excelente tiempo! Menos de 2 segundos")
    elif tiempo_total < 4000:
        print("   👍 Buen tiempo, entre 2 y 4 segundos")
    else:
        print("   ⏳ Tiempo un poco largo, más de 4 segundos")
    
    return tiempo_total

# Ejecutar simulación
tiempo_juego = simular_juego()

print("\n" + "="*50)
print("RESUMEN DE PRUEBAS")
print("="*50)
print("✅ Todas las pruebas completadas")
print(f"⏱️  Último tiempo de juego: {tiempo_juego} ms")

# Mostrar tiempo en diferentes formatos
buffer_final = ffi.new("char[]", 20)
lib.formato_tiempo_mm_ss(tiempo_juego, buffer_final)
print(f"📊 Tiempo formateado: {ffi.string(buffer_final).decode()}")

# Convertir a minutos y segundos para mostrar
minutos = tiempo_juego // 60000
segundos = (tiempo_juego % 60000) // 1000
milisegundos = tiempo_juego % 1000
print(f"⏰ Desglose: {minutos:02d}:{segundos:02d}.{milisegundos:03d}")

print("\n🎉 ¡Pruebas finalizadas correctamente!")