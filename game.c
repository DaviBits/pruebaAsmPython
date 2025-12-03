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
void obtenerLineaRandom(char *buffer, char *out);
int leerArchivo(const char *nombre, char *buffer, int max);

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
        mov edx, 0       ; ← FIX IMPORTANTE
        div ecx            ; edx = eax % max

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

int leerArchivo(const char *nombre, char *buffer, int max)
{
    char modoLectura[] = "r";
    int n;
    FILE *f;

    __asm {
        ; f = fopen(nombre, "r")
        push offset modoLectura
        push nombre
        call fopen
        add esp, 8
        mov f, eax

        ; if (!f) return 0
        test eax, 0
        jnz archivo_ok
        cmp eax, 0
        mov n, eax
        jmp fin

    archivo_ok:

        ; n = fread(buffer, 1, max-1, f)
        mov eax, max
        dec eax
        push f
        push eax
        push 1
        push buffer
        call fread
        add esp, 16
        mov n, eax

        ; buffer[n] = '\0'
        mov edx, buffer
        add edx, eax
        mov byte ptr [edx], 0

        ; fclose(f)
        push f
        call fclose
        add esp, 4

    fin:
    }

    return n;
}




void obtenerLineaRandom(char *buffer, char *out) {
    __asm {
        mov esi, buffer
        mov edi, out
        xor ecx, ecx               ; ECX = contador de saltos '\n'

    ; ============================
    ; CONTAR LÍNEAS
    ; ============================
    contar_lineas:
        mov al, [esi]
        cmp al, 0
        je fin_conteo              ; fin del buffer

        cmp al, 0Ah                ; si es '\n'
        jne seguir_contar
        inc ecx                    ; contamos un salto → una línea

    seguir_contar:
        inc esi
        jmp contar_lineas

    fin_conteo:
        inc ecx                    ; total líneas = saltos+1

        ; generar índice aleatorio en [0, ecx-1]
        push ecx
        call rnd
        add esp, 4
        mov ebx, eax               ; EBX = línea objetivo

        mov esi, buffer

    ; ============================
    ; BUSCAR INICIO DE LA LÍNEA SELECCIONADA
    ; ============================
    buscar_linea:
        cmp ebx, 0
        je copiar_linea

        mov al, [esi]
        cmp al, 0
        je copiar_linea            ; EOF inesperado

        cmp al, 0Ah
        jne avanzar_busqueda
        dec ebx                    ; llegó a un salto → próxima línea

    avanzar_busqueda:
        inc esi
        jmp buscar_linea

    ; ============================
    ; COPIAR LA LÍNEA (ignorando '\r')
    ; ============================
    copiar_linea:
        mov al, [esi]
        cmp al, 0
        je fin

        cmp al, 0Ah                ; fin de la línea
        je fin

        cmp al, 0Dh                ; ignorar '\r'
        je ignorar_cr

        mov [edi], al              ; copiar caracter
        inc edi

    ignorar_cr:
        inc esi
        jmp copiar_linea

    fin:
        mov byte ptr [edi], 0      ; terminador
    }
}

int contarLineas(char *buffer) {
    int total = 0;

    __asm {
        mov esi, buffer
        xor ecx, ecx    ; contador de saltos '\n' = 0

    cl_loop:
        mov al, [esi]
        cmp al, 0
        je cl_fin

        cmp al, 0Ah     ; '\n'
        jne cl_next
        inc ecx

    cl_next:
        inc esi
        jmp cl_loop

    cl_fin:
        inc ecx         ; número real de líneas = saltos + 1
        mov total, ecx
    }

    return total;
}

