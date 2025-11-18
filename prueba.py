import _add_lib

lib = _add_lib.lib

a = 5
b = 7
resultado_asm = lib.add_asm(a, b)
resultado_c = lib.add_c(a, b)

print("Resultado add_asm:", resultado_asm)  # 12
print("Resultado add_c:", resultado_c)      # 12
print("Resultado sub_asm:", lib.sub_asm(b, a))  # 2
print("Resultado mul_asm:", lib.mul_asm(a, b))  # 35