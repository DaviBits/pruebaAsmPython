#include <stdio.h>
#include <time.h>
#include <stdlib.h>   
#include <Windows.h>

static unsigned int global_seed = 0;
static DWORD tiempo_inicio = 0;
static DWORD tiempo_total = 0;

int rnd(int max);
int cmpCad(char cad1[], char cad2[]);
int charInCad(char car, char cad[]);
int lenCad(char cad[]);
void mezclarCadena(char cad[]);
void init_rand_seed();
void obtenerLineaRandom(char *buffer, char *out);
int leerArchivo(const char *nombre, char *buffer, int max);
int contarLineas(char *buffer);
int letraEnPosicion(char letra, const char* palabra, int posicion);
int contarOcurrencias(char letra, const char* palabra);
void obtenerPista(const char* palabra, const char* palabraOculta, char* resultado);
int cmpCadIgnoreCase(const char* cad1, const char* cad2);
void letrasUnicas(const char* palabra, char* resultado);
void iniciar_temporizador();
DWORD detener_temporizador();
DWORD obtener_tiempo_actual();
void formato_tiempo_mm_ss(DWORD ms, char* buffer);


void init_rand_seed() {  // Inicializa la semilla para números aleatorios
    global_seed = (unsigned int)time(NULL) ^ (unsigned int)getpid();
}

void iniciar_temporizador() {  // Inicia el temporizador
    __asm {
        call GetTickCount
        mov tiempo_inicio, eax
    }
}

DWORD detener_temporizador() {  // Detiene el temporizador y devuelve tiempo transcurrido
    DWORD tiempo_transcurrido;
    
    __asm {
        call GetTickCount
        sub eax, tiempo_inicio
        mov tiempo_transcurrido, eax
        add tiempo_total, eax
    }
    
    return tiempo_transcurrido;
}

DWORD obtener_tiempo_actual() {  // Obtiene tiempo actual sin detener
    DWORD tiempo_actual;
    
    __asm {
        call GetTickCount
        sub eax, tiempo_inicio
        mov tiempo_actual, eax
    }
    
    return tiempo_actual;
}

void formato_tiempo_mm_ss(DWORD ms, char* buffer) {  // Formatea tiempo a "MM:SS"
    __asm {
        push ebx
        push esi
        push edi
        
        mov eax, ms
        mov edi, buffer
        
        xor edx, edx
        mov ecx, 60000
        div ecx
        
        mov bl, 10
        div bl
        
        add al, '0'
        mov [edi], al
        add ah, '0'
        mov [edi+1], ah
        mov byte ptr [edi+2], ':'
        
        mov eax, edx
        xor edx, edx
        mov ecx, 1000
        div ecx
        
        mov bl, 10
        div bl
        
        add al, '0'
        mov [edi+3], al
        add ah, '0'
        mov [edi+4], ah
        mov byte ptr [edi+5], 0
        
        pop edi
        pop esi
        pop ebx
    }
}

int rnd(int max){  // Genera número aleatorio entre 0 y max-1
     int resultado;
    
    __asm {
        call GetTickCount
        mov ecx, 1664525
        imul ecx
        add eax, 1013904223
        
        xor edx, edx
        mov ecx, max
        test ecx, ecx
        jz fin
        div ecx
        mov resultado, edx
        jmp fin
        
        fin:
    }
    
    return resultado;
}

int cmpCad(char cad1[], char cad2[]) {  // Compara dos cadenas
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

int charInCad(char car, char cad[]) {  // Verifica si un carácter está en una cadena
    int contCar = 1;

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

int lenCad(char cad[]) {  // Obtiene longitud de una cadena
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

void mezclarCadena(char cad[]) {  // Mezcla aleatoriamente una cadena
    __asm {
        push esi
        push edi
        push ebx

        mov esi, cad

        push cad
        call lenCad
        add esp, 4
        mov ecx, eax
        dec ecx

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

int leerArchivo(const char *nombre, char *buffer, int max) {  // Lee contenido de archivo
    FILE *f = fopen(nombre, "r");
    if (!f) return 0;

    int n = fread(buffer, 1, max-1, f);
    buffer[n] = 0; 

    fclose(f);
    return n;
}

void obtenerLineaRandom(char *buffer, char *out) {  // Obtiene una línea aleatoria del buffer
    __asm {
        mov esi, buffer
        mov edi, out
        xor ecx, ecx

    contar_lineas:
        mov al, [esi]
        cmp al, 0
        je fin_conteo

        cmp al, 0Ah
        jne seguir_contar
        inc ecx

    seguir_contar:
        inc esi
        jmp contar_lineas

    fin_conteo:
        inc ecx

        push ecx
        call rnd
        add esp, 4
        mov ebx, eax

        mov esi, buffer

    buscar_linea:
        cmp ebx, 0
        je copiar_linea

        mov al, [esi]
        cmp al, 0
        je copiar_linea

        cmp al, 0Ah
        jne avanzar_busqueda
        dec ebx

    avanzar_busqueda:
        inc esi
        jmp buscar_linea

    copiar_linea:
        mov al, [esi]
        cmp al, 0
        je fin

        cmp al, 0Ah
        je fin

        cmp al, 0Dh
        je ignorar_cr

        mov [edi], al
        inc edi

    ignorar_cr:
        inc esi
        jmp copiar_linea

    fin:
        mov byte ptr [edi], 0
    }
}

int contarLineas(char *buffer) {  // Cuenta líneas en buffer
    int total = 0;

    __asm {
        mov esi, buffer
        xor ecx, ecx

    cl_loop:
        mov al, [esi]
        cmp al, 0
        je cl_fin

        cmp al, 0Ah
        jne cl_next
        inc ecx

    cl_next:
        inc esi
        jmp cl_loop

    cl_fin:
        inc ecx
        mov total, ecx
    }

    return total;
}

int letraEnPosicion(char letra, const char* palabra, int posicion) {  // Verifica letra en posición
    int resultado = 0;
    
    __asm {
        mov al, [ebp+8]
        mov esi, [ebp+12]
        mov ecx, [ebp+16]
        mov resultado, 0
        
        cmp ecx, 0
        jl fin_letraPos
        
        xor ebx, ebx
        
    buscar_posicion:
        mov dl, [esi+ebx]
        cmp dl, 0
        je fin_letraPos
        
        cmp ebx, ecx
        je verificar_letra
        
        inc ebx
        jmp buscar_posicion

    verificar_letra:
        cmp al, dl
        jne fin_letraPos
        
        mov resultado, 1
        jmp fin_letraPos

    fin_letraPos:
    }
    
    return resultado;
}

int contarOcurrencias(char letra, const char* palabra) {  // Cuenta ocurrencias de letra
    int cuantas = 0;
    
    __asm {
        mov al, [ebp+8]
        mov esi, [ebp+12]
        xor ecx, ecx

    ciclo_contar:
        mov dl, [esi]
        cmp dl, 0
        je fin_contar
        
        cmp al, dl
        jne siguiente_char
        
        inc ecx

    siguiente_char:
        inc esi
        jmp ciclo_contar

    fin_contar:
        mov cuantas, ecx
    }
    
    return cuantas;
}

void obtenerPista(const char* palabra, const char* palabraOculta, char* resultado) {  // Obtiene pista revelando letra oculta
    __asm {
        push ebx
        push edi
        push esi
        
        mov esi, [ebp+8]
        mov edi, [ebp+12]
        mov ebx, [ebp+16]
        
        xor ecx, ecx
        
    copiar_ciclo:
        mov al, [edi+ecx]
        mov [ebx+ecx], al
        inc ecx
        test al, al
        jnz copiar_ciclo
        
        dec ecx
        jle fin_pista
        
        push ecx
        call rand
        pop ecx
        
        xor edx, edx
        div ecx
        
        mov eax, edx
        xor edx, edx
        
    buscar_oculta:
        cmp byte ptr [edi+eax], '_'
        jne siguiente_posicion
        
        mov cl, [esi+eax]
        mov [ebx+eax], cl
        jmp fin_pista

    siguiente_posicion:
        inc eax
        inc edx
        cmp edx, ecx
        jl buscar_siguiente
        
        xor eax, eax
        xor edx, edx
        
    buscar_siguiente:
        cmp edx, ecx
        jl buscar_oculta

    fin_pista:
        pop esi
        pop edi
        pop ebx
    }
}

int cmpCadIgnoreCase(const char* cad1, const char* cad2) {  // Compara cadenas ignorando mayúsculas/minúsculas
    int iguales = 1;
    
    __asm {
        push ebx
        push edi
        push esi
        
        mov esi, [ebp+8]
        mov edi, [ebp+12]
        
        mov iguales, 1

    comparar_ciclo:
        mov al, [esi]
        mov bl, [edi]
        
        test al, al
        jz verificar_fin_cad2
        test bl, bl
        jz no_iguales
        
        cmp al, 'a'
        jb check_cad1_upper
        cmp al, 'z'
        ja check_cad1_upper
        sub al, 32

    check_cad1_upper:
        cmp bl, 'a'
        jb comparar_chars
        cmp bl, 'z'
        ja comparar_chars
        sub bl, 32

    comparar_chars:
        cmp al, bl
        jne no_iguales
        
        inc esi
        inc edi
        jmp comparar_ciclo

    verificar_fin_cad2:
        cmp byte ptr [edi], 0
        jne no_iguales
        
        jmp salir_cmp

    no_iguales:
        mov iguales, 0

    salir_cmp:
        pop esi
        pop edi
        pop ebx
    }
    
    return iguales;
}

void letrasUnicas(const char* palabra, char* resultado) {  // Obtiene letras únicas de palabra
    __asm {
        push ebp
        mov ebp, esp
        push ebx
        push edi
        push esi
        
        mov esi, [ebp+8]
        mov edi, [ebp+12]
        sub esp, 26
        mov ebx, esp
        xor eax, eax
        mov ecx, 26
        mov edx, ebx
    inicializar_tabla:
        mov byte ptr [edx], al
        inc edx
        loop inicializar_tabla
    procesar_palabra:
        mov al, [esi]
        test al, al
        jz construir_resultado
        
        cmp al, 'a'
        jb check_letra
        cmp al, 'z'
        ja check_letra
        sub al, 32

    check_letra:
        cmp al, 'A'
        jb siguiente_letra
        cmp al, 'Z'
        ja siguiente_letra
        sub al, 'A'
        movzx cx, al 
        mov byte ptr [ebx+ecx], 1

    siguiente_letra:
        inc esi
        jmp procesar_palabra

    construir_resultado:
        xor ecx, ecx
        xor edx, edx
        
    construir_ciclo:
        cmp edx, 26
        jge fin_unicas
        
        cmp byte ptr [ebx+edx], 0
        je siguiente_indice
        
        mov al, dl
        add al, 'A'
        mov [edi+ecx], al
        inc ecx

    siguiente_indice:
        inc edx
        jmp construir_ciclo

    fin_unicas:
        mov byte ptr [edi+ecx], 0
        
        add esp, 26
        
        pop esi
        pop edi
        pop ebx
        pop ebp
    }
}