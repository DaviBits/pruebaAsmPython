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


void init_rand_seed() {
    global_seed = (unsigned int)time(NULL) ^ (unsigned int)getpid();
}

void iniciar_temporizador() {
    __asm {
        call GetTickCount      ; Llama a la función de Windows
        mov tiempo_inicio, eax ; Guarda el tiempo de inicio
    }
}

// ============================================
// 2. DETENER TEMPORIZADOR Y OBTENER TIEMPO
// ============================================
DWORD detener_temporizador() {
    DWORD tiempo_transcurrido;
    
    __asm {
        call GetTickCount          ; Obtiene tiempo actual
        sub eax, tiempo_inicio     ; Resta tiempo de inicio
        mov tiempo_transcurrido, eax ; Guarda resultado
        
        ; Opcional: sumar al tiempo total
        add tiempo_total, eax
    }
    
    return tiempo_transcurrido;  // Milisegundos
}

// ============================================
// 3. OBTENER TIEMPO ACTUAL SIN DETENER
// ============================================
DWORD obtener_tiempo_actual() {
    DWORD tiempo_actual;
    
    __asm {
        call GetTickCount
        sub eax, tiempo_inicio
        mov tiempo_actual, eax
    }
    
    return tiempo_actual;
}

// ============================================
// 4. FUNCIÓN PARA FORMATO "MM:SS"
// ============================================
void formato_tiempo_mm_ss(DWORD ms, char* buffer) {
    __asm {
        push ebx
        push esi
        push edi
        
        mov eax, ms           ; Milisegundos a convertir
        mov edi, buffer       ; Buffer de salida
        
        ; ---- CALCULAR MINUTOS ----
        ; minutos = ms / 60000
        xor edx, edx
        mov ecx, 60000        ; 60 segundos * 1000 ms
        div ecx               ; EAX = minutos, EDX = ms restantes
        
        ; Formatear minutos (2 dígitos)
        mov bl, 10
        div bl                ; AL = decenas, AH = unidades
        
        add al, '0'
        mov [edi], al         ; Primer dígito
        add ah, '0'
        mov [edi+1], ah       ; Segundo dígito
        mov byte ptr [edi+2], ':' ; Separador
        
        ; ---- CALCULAR SEGUNDOS ----
        ; segundos = ms_restantes / 1000
        mov eax, edx          ; ms restantes
        xor edx, edx
        mov ecx, 1000
        div ecx               ; EAX = segundos
        
        ; Formatear segundos (2 dígitos)
        mov bl, 10
        div bl
        
        add al, '0'
        mov [edi+3], al       ; Primer dígito segundos
        add ah, '0'
        mov [edi+4], ah       ; Segundo dígito segundos
        mov byte ptr [edi+5], 0 ; Null terminator
        
        pop edi
        pop esi
        pop ebx
    }
}

int rnd(int max){
     int resultado;
    
    __asm {
        // Llamar a GetTickCount
        call GetTickCount  ; EAX = milisegundos desde boot
        
        // Usar como semilla para generador aleatorio
        mov ecx, 1664525
        imul ecx          ; EDX:EAX = EAX * ECX
        add eax, 1013904223
        
        // Aplicar módulo
        xor edx, edx
        mov ecx, max
        test ecx, ecx
        jz fin
        div ecx           ; EDX = EAX % ECX
        mov resultado, edx
        jmp fin
        
        fin:
    }
    
    return resultado;
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

int leerArchivo(const char *nombre, char *buffer, int max) {
    FILE *f = fopen(nombre, "r");
    if (!f) return 0;

    int n = fread(buffer, 1, max-1, f);
    buffer[n] = 0; 

    fclose(f);
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

int letraEnPosicion(char letra, const char* palabra, int posicion) {
    int resultado = 0;
    
    __asm {
        mov al, [ebp+8]      ; char letra
        mov esi, [ebp+12]    ; const char* palabra
        mov ecx, [ebp+16]    ; int posicion
        mov resultado, 0     ; resultado inicial = 0
        
        ; Verificar si la posición es válida (no negativa)
        cmp ecx, 0
        jl fin_letraPos
        
        ; Buscar la posición en la cadena
        xor ebx, ebx         ; contador de posición actual
        
    buscar_posicion:
        mov dl, [esi+ebx]
        cmp dl, 0
        je fin_letraPos      ; Fin de cadena alcanzado
        
        cmp ebx, ecx
        je verificar_letra   ; Llegamos a la posición deseada
        
        inc ebx
        jmp buscar_posicion

    verificar_letra:
        ; Comparar la letra en esa posición
        cmp al, dl
        jne fin_letraPos
        
        ; Coincidencia encontrada
        mov resultado, 1
        jmp fin_letraPos

    fin_letraPos:
        ; El resultado ya está en la variable
    }
    
    return resultado;
}

int contarOcurrencias(char letra, const char* palabra) {
    int cuantas = 0;
    
    __asm {
        mov al, [ebp+8]      ; char letra
        mov esi, [ebp+12]    ; const char* palabra
        xor ecx, ecx         ; contador = 0

    ciclo_contar:
        mov dl, [esi]
        cmp dl, 0
        je fin_contar
        
        cmp al, dl
        jne siguiente_char
        
        ; Encontrada coincidencia
        inc ecx

    siguiente_char:
        inc esi
        jmp ciclo_contar

    fin_contar:
        mov cuantas, ecx
    }
    
    return cuantas;
}

void obtenerPista(const char* palabra, const char* palabraOculta, char* resultado) {
    __asm {
        push ebx
        push edi
        push esi
        
        mov esi, [ebp+8]     ; const char* palabra
        mov edi, [ebp+12]    ; const char* palabraOculta
        mov ebx, [ebp+16]    ; char* resultado
        
        ; Primero, copiar palabraOculta a resultado
        xor ecx, ecx         ; índice
        
    copiar_ciclo:
        mov al, [edi+ecx]
        mov [ebx+ecx], al
        inc ecx
        test al, al
        jnz copiar_ciclo
        
        ; Ahora buscar posiciones ocultas (guiones bajos '_')
        dec ecx              ; longitud - 1 (sin contar el null)
        jle fin_pista        ; Si longitud <= 1, no hacer nada
        
        ; Generar posición aleatoria entre 0 y ecx-1
        push ecx
        call rand
        pop ecx
        
        ; eax contiene número aleatorio, hacer módulo ecx
        xor edx, edx
        div ecx              ; edx = eax % ecx (posición aleatoria)
        
        ; Buscar desde la posición aleatoria una letra oculta
        mov eax, edx         ; posición inicial aleatoria
        xor edx, edx         ; contador de intentos
        
    buscar_oculta:
        ; Verificar si en esta posición hay '_'
        cmp byte ptr [edi+eax], '_'
        jne siguiente_posicion
        
        ; Encontrada posición oculta, revelar letra
        mov cl, [esi+eax]    ; letra original
        mov [ebx+eax], cl    ; poner en resultado
        jmp fin_pista

    siguiente_posicion:
        inc eax
        inc edx
        cmp edx, ecx
        jl buscar_siguiente
        
        ; Si llegamos aquí, buscar desde el principio
        xor eax, eax
        xor edx, edx
        
    buscar_siguiente:
        ; Verificar si hemos revisado todas las posiciones
        cmp edx, ecx
        jl buscar_oculta

    fin_pista:
        pop esi
        pop edi
        pop ebx
    }
}

int cmpCadIgnoreCase(const char* cad1, const char* cad2) {
    int iguales = 1;
    
    __asm {
        push ebx
        push edi
        push esi
        
        mov esi, [ebp+8]     ; const char* cad1
        mov edi, [ebp+12]    ; const char* cad2
        
        mov iguales, 1       ; asumir iguales

    comparar_ciclo:
        mov al, [esi]
        mov bl, [edi]
        
        ; Si ambos son null, fin de cadenas iguales
        test al, al
        jz verificar_fin_cad2
        test bl, bl
        jz no_iguales
        
        ; Convertir a mayúsculas si es minúscula
        cmp al, 'a'
        jb check_cad1_upper
        cmp al, 'z'
        ja check_cad1_upper
        sub al, 32           ; Convertir a mayúscula

    check_cad1_upper:
        ; Hacer lo mismo para bl
        cmp bl, 'a'
        jb comparar_chars
        cmp bl, 'z'
        ja comparar_chars
        sub bl, 32           ; Convertir a mayúscula

    comparar_chars:
        cmp al, bl
        jne no_iguales
        
        inc esi
        inc edi
        jmp comparar_ciclo

    verificar_fin_cad2:
        ; Verificar si cad2 también terminó
        cmp byte ptr [edi], 0
        jne no_iguales
        
        ; Cadenas iguales
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

void letrasUnicas(const char* palabra, char* resultado) {
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
        
        ; Agregar letra al resultado
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

