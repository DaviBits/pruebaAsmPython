#ifndef _GAME_SIMPLE_
#define _GAME_SIMPLE_

// Usar unsigned int en lugar de DWORD (es lo mismo en Windows 32-bit)
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

// Funciones de temporizador (usando unsigned int)
void iniciar_temporizador();
unsigned int detener_temporizador();
unsigned int obtener_tiempo_actual();
void formato_tiempo_mm_ss(unsigned int ms, char* buffer);

#endif