from cffi import FFI

CDEF = '''
int add_c(int, int);
int add_asm(int, int);
int sub_asm(int, int);
int mul_asm(int, int);
'''

ffibuilder = FFI()
ffibuilder.cdef(CDEF)

ffibuilder.set_source(
    "_add_lib",
    '#include "add.h"',
    sources=['add.c'],
    include_dirs=['.']
)

ffibuilder.compile(verbose=True)
