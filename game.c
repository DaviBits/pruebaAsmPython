

#include <stdio.h>
#include <time.h>
#include <stdlib.h>   
static unsigned int global_seed = 0;
int rnd(int max);
int cmpCad(char cad1[], char cad2[]);
int charInCad(char car, char cad[]);
int lenCad(char cad[]);
void mezclarCadena(char cad[]);
void init_rand_seed();

void init_rand_seed() {
    global_seed = (unsigned int)time(NULL) ^ (unsigned int)getpid();
}

int rnd(int max){
    int selected = 0;
    
    __asm{
        mov eax, global_seed
        imul eax, 1664525
        add eax, 1013904223
        mov global_seed, eax 

        mov ecx, max
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
        push esi
        push edi
        push ebx

        mov esi, cad

        ; obtener longitud : lenCad(cad)
        push cad
        call lenCad
        add esp, 4; limpiar argumento
        mov ecx, eax; ecx = longitud
        dec ecx; ecx = longitud - 1

        cmp ecx, 0
        jl mez_end

        mez_loop :
        mov ebx, ecx
            inc ebx

            push ecx
            push ebx
            call rnd
            add esp, 4
            pop ecx
            mov edi, eax

            mov al, [esi + ecx]
            mov bl, [esi + edi]
            mov[esi + ecx], bl
            mov[esi + edi], al

            dec ecx
            cmp ecx, 0
            jge mez_loop

            mez_end :
        pop ebx
            pop edi
            pop esi
    }
}







