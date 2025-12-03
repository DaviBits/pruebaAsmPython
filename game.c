

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

int cmpCad(char cad1[], char cad2[]) { 
    int esLaMisma = 1;

    __asm {
        mov esi, cad1
        mov edi, cad2

        push esi
        call lenCad
        add esp, 4
        mov ecx, eax

        push edi
        call lenCad
        add esp, 4
        cmp ecx, eax
        jne diferente

        mov esi, cad1
        mov edi, cad2

    comparar:
        mov al, [esi]
        mov bl, [edi]
        cmp al, bl
        jne diferente
        inc esi
        inc edi
        loop comparar

        jmp iguales

    iguales:
        mov esLaMisma, 1
        jmp fin

    diferente:
        mov esLaMisma, 0

    fin:
    }

    return esLaMisma;
}


int charInCad(char car, char cad[]) { // caracter, cadena
    int contCar = 1;   // 1 sí lo contiene, 0  no

    __asm {
        mov al, car 
        mov esi, cad
    buscar:
        mov bl, [esi]
        cmp bl, 0
        je  noEncontrado
        cmp al, bl
        je  encontrado
        inc esi
        jmp buscar
    encontrado:
        mov contCar, 1
        jmp fin

    noEncontrado:
        mov contCar, 0

    fin:
    }

    return contCar;
}

int lenCad(char cad[]) {
    int len = 0;
    __asm {
        mov esi, cad
        contar:
            mov al, [esi]
            cmp al, 0
            je longitudLista
            inc esi
            jmp contar
        longitudLista:
        sub esi, cad
        mov len, esi
    }

    return len;
}

void mezclarCadena(char cad[]) {
    __asm {
        mov esi, cad
        mov ecx, len
        dec ecx

        loop_fy:
            mov ebx, ecx
            inc ebx

            push ebx
            call rnd
            add esp, 4

            mov edi, eax 

            mov al, [esi + ecx]
            mov bl, [esi + edi]

            mov [esi + ecx], bl
            mov [esi + edi], al

            dec ecx
            jns loop_fy
    }
}


