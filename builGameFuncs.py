from cffi import FFI

CDEF = '''
int rnd(int);
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
