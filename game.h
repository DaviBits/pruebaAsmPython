#ifndef _GAME_
#define _GAME_

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

#endif
