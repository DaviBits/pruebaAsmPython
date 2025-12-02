 int add_asm(int a, int b){
    int resul;
    __asm{
        mov eax, a
        add eax, b
        mov resul, eax
    }
    return resul;
 }

int sub_asm(int a, int b){
    int resul;
    __asm{
        mov eax, a
        sub eax, b
        mov resul, eax
    }
    return resul;
 }

 int mul_asm(int a, int b){
    int result;
    __asm{
        mov eax, a
        mul b
        mov result, eax
    }
    return result;
 }



int add_c(int a, int b) {
    return add_asm(a, b);
}