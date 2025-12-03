.386
.model flat, stdcall
option casemap:none

PUBLIC Sumar       ; tu función de ejemplo
PUBLIC DllMain     ; obligatorio para linkear DLL

.code

; ----------------------------
; Función de prueba: suma dos números
; int Sumar(int a, int b)
; ----------------------------
Sumar PROC a:DWORD, b:DWORD
    mov eax, a
    add eax, b
    ret
Sumar ENDP

; ----------------------------
; DllMain mínimo (obligatorio)
; ----------------------------
DllMain PROC hinstDLL:DWORD, fdwReason:DWORD, lpvReserved:DWORD
    mov eax, 1   ; TRUE
    ret
DllMain ENDP

END
