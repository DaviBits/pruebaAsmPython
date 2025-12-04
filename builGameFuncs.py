from cffi import FFI

CDEF = '''
int rnd(int max);
int lenCad(char* cad);
int cmpCad(char* a, char* b);
int charInCad(char c, char* cad);
void mezclarCadena(char* cad);
void init_rand_seed();
void obtenerLineaRandom(char *buffer, char *out);
int leerArchivo(const char *nombre, char *buffer, int max);
int contarLineas(char *buffer);
int letraEnPosicion(char letra, const char* palabra, int posicion);
int contarOcurrencias(char letra, const char* palabra);
void obtenerPista(const char* palabra, const char* palabraOculta, char* resultado);
int cmpCadIgnoreCase(const char* cad1, const char* cad2);
void letrasUnicas(const char* palabra, char* resultado);

// Temporizador con unsigned int
void iniciar_temporizador();
unsigned int detener_temporizador();
unsigned int obtener_tiempo_actual();
void formato_tiempo_mm_ss(unsigned int ms, char* buffer);
'''

ffibuilder = FFI()
ffibuilder.cdef(CDEF)

ffibuilder.set_source(
    "_game_lib",
    '#include "game.h"',
    sources=['game.c'],
    include_dirs=['.'],
    libraries=['kernel32', 'winmm']  # kernel32 para GetTickCount
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)