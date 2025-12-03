from cffi import FFI

CDEF = '''
int rnd(int);
int lenCad(char* cad);
int cmpCad(char* a, char* b);
int charInCad(char c, char* cad);
void mezclarCadena(char* cad);
void init_rand_seed();
'''

ffibuilder = FFI()
ffibuilder.cdef(CDEF)

ffibuilder.set_source(
    "_game_lib",
    '#include "game.h"',
    sources=['game.c'],
    include_dirs=['.']
)

ffibuilder.compile(verbose=True)
