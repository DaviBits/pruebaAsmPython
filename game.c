

#include <stdio.h>

int rnd(int max){
    int selected = 0;
    static unsigned int seed = 12345678;

    __asm{
        mov eax, seed
        imul eax, 1664525
        add eax, 1013904223
        mov seed, eax

        mov ecx, max      ; <<< ESTA ES LA MANERA CORRECTA EN MSVC
        mov edx, 0
        div ecx

        mov selected, edx
    }

    return selected;
}