import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from cffi import FFI
import _game_lib

# ============================
#  CONEXIÓN C/ASM
# ============================
lib = _game_lib.lib
ffi = FFI()
lib.init_rand_seed()

BASE = os.path.abspath(os.path.dirname(__file__))

ARCHIVOS = [
    os.path.join(BASE, "niveles", "facil.txt").encode(),
    os.path.join(BASE, "niveles", "medio.txt").encode(),
    os.path.join(BASE, "niveles", "dificil.txt").encode(),
]

def obtener_categoria(dificultad: int) -> str:
    txt_buffer = ffi.new("char[]", 4096)
    categoria = ffi.new("char[]", 256)

    leidos = lib.leerArchivo(ARCHIVOS[dificultad], txt_buffer, 4096)
    if leidos <= 0:
        raise FileNotFoundError("No se pudo leer archivo")

    lib.obtenerLineaRandom(txt_buffer, categoria)
    return ffi.string(categoria).decode().strip()


# ============================
#  GUI
# ============================
class InterfazDemo:
    def __init__(self, root, dificultad=0):
        self.root = root
        root.title("4 Imágenes 1 Palabra - Demo")
        root.geometry("850x900")
        root.configure(bg="#1e1e1e")

        self.color_bg = "#1e1e1e"
        self.color_panel = "#2b2b2b"
        self.color_btn = "#4caf50"
        self.color_text = "#ffffff"
        self.color_correct = "#4caf50"
        self.color_incorrect = "#ff4444"
        self.color_partial = "#ffa500"

        # Palabra correcta desde C/ASM
        self.categoria = obtener_categoria(dificultad)
        print("Palabra/frase elegida:", self.categoria)

        self.carpeta = os.path.join(BASE, "Imagenes", self.categoria)

        # TÍTULO
        tk.Label(
            root,
            text=f"Adivina la palabra/frase",
            font=("Helvetica", 28, "bold"),
            bg=self.color_bg,
            fg=self.color_text
        ).pack(pady=20)

        # IMÁGENES
        frame_imgs = tk.Frame(root, bg=self.color_panel, bd=2, relief="ridge")
        frame_imgs.pack(pady=15)

        if dificultad == 0:
            rutas = [
                os.path.join(self.carpeta, "img1.png"),
                os.path.join(self.carpeta, "img2.png"),
                os.path.join(self.carpeta, "img3.png"),
                os.path.join(self.carpeta, "img4.png")
            ]
        else:
            rutas = [
                os.path.join(self.carpeta, "img1.png"),
                os.path.join(self.carpeta, "img2.png")
            ]

        self.imagenes_tk = []
        for i, ruta in enumerate(rutas):
            try:
                img = Image.open(ruta).resize((150, 150))
                tk_img = ImageTk.PhotoImage(img)
                lbl = tk.Label(frame_imgs, image=tk_img, bg=self.color_panel)
                lbl.image = tk_img
                lbl.grid(row=i // 2, column=i % 2, padx=10, pady=10)
                self.imagenes_tk.append(tk_img)
            except Exception as e:
                print(f"Error cargando imagen {ruta}: {e}")
                lbl = tk.Label(frame_imgs, text="No img", bg=self.color_panel, fg="white")
                lbl.grid(row=i // 2, column=i % 2, padx=10, pady=10)

        # SLOTS
        self.word = self.categoria.upper()
        self.slots = []
        
        # Usar lenCad para obtener el número de slots (sin contar espacios)
        palabra_sin_espacios = "".join(ch for ch in self.word if ch != " ")
        palabra_sin_espacios_b = palabra_sin_espacios.encode()
        num_slots = lib.lenCad(palabra_sin_espacios_b)
        
        self.letras_bloqueadas = [False] * num_slots
        
        # Frame principal para slots
        frame_slots = tk.Frame(root, bg=self.color_bg)
        frame_slots.pack(pady=20, fill="both", expand=True)
        
        self.crear_slots_organizados(frame_slots)

        # ================================
        # ENTRADA POR TECLADO
        # ================================
        tk.Label(
            root,
            text="Ingresa letras por teclado o haz click en los slots para remover letras",
            font=("Helvetica", 12),
            bg=self.color_bg,
            fg=self.color_text
        ).pack(pady=10)

        # Frame para mostrar letras disponibles
        frame_info = tk.Frame(root, bg=self.color_bg)
        frame_info.pack(pady=10)

        # Obtener letras únicas de la palabra usando charInCad
        palabra_sin_espacios = self.word.replace(" ", "")
        palabra_sin_espacios_b = palabra_sin_espacios.encode()
        letras_unicas = set()
        
        for letra_code in range(65, 91):  # A-Z
            letra = chr(letra_code)
            letra_b = letra.encode()
            
            if lib.charInCad(letra_b, palabra_sin_espacios_b) == 1:
                letras_unicas.add(letra)

        # Rellenar hasta al menos 12 letras únicas usando lib.rnd
        abecedario = [chr(i) for i in range(65, 91)]
        letras_finales = list(letras_unicas)
        
        # Usar lenCad indirectamente para la condición del while
        letras_finales_str = "".join(letras_finales)
        letras_finales_b = letras_finales_str.encode()
        
        while lib.lenCad(letras_finales_b) < 12:
            # Usar lib.rnd para obtener índice aleatorio
            idx = lib.rnd(25)  # 0-25
            nueva = abecedario[idx]
            if nueva not in letras_finales:
                letras_finales.append(nueva)
                letras_finales_str = "".join(letras_finales)
                letras_finales_b = letras_finales_str.encode()

        # Revolver las letras usando mezclarCadena
        letras_str = "".join(letras_finales)
        buf = ffi.new("char[]", letras_str.encode())
        lib.mezclarCadena(buf)
        self.letras_disponibles = ffi.string(buf).decode()

        # Mostrar letras disponibles usando lenCad para mostrar longitud
        letras_disponibles_len = lib.lenCad(self.letras_disponibles.encode())
        tk.Label(
            frame_info,
            text=f"Letras disponibles ({letras_disponibles_len}): {self.letras_disponibles}",
            font=("Helvetica", 14, "bold"),
            bg=self.color_bg,
            fg="#4caf50"
        ).pack()

        # Botón para validar
        self.btn_validar = tk.Button(
            root,
            text="VALIDAR",
            font=("Helvetica", 16, "bold"),
            bg="#4caf50",
            fg="white",
            relief="raised",
            command=self.validar
        )
        self.btn_validar.pack(pady=20)

        # Configurar bindings del teclado
        self.root.bind("<Key>", self.manejar_tecla)

    def crear_slots_organizados(self, parent_frame):
        """Crea slots organizados en filas"""
        self.slots = []
        
        main_slot_frame = tk.Frame(parent_frame, bg=self.color_bg)
        main_slot_frame.pack()
        
        max_slots_por_fila = 15
        fila_actual = 0
        columna_actual = 0
        current_row_frame = None
        
        # Convertir palabra a bytes para usar lenCad
        palabra_b = self.word.encode()
        longitud_total = lib.lenCad(palabra_b)
        
        for i in range(longitud_total):
            # Obtener carácter actual - usando lenCad para verificar límites
            if i < lib.lenCad(palabra_b):
                ch = self.word[i]
            else:
                ch = ""
            
            if columna_actual == 0 or columna_actual >= max_slots_por_fila:
                if current_row_frame:
                    current_row_frame.pack()
                
                current_row_frame = tk.Frame(main_slot_frame, bg=self.color_bg)
                current_row_frame.pack(pady=5)
                columna_actual = 0
                fila_actual += 1
            
            if ch == " ":
                spacer = tk.Label(
                    current_row_frame,
                    text="   ",
                    font=("Helvetica", 24),
                    bg=self.color_bg,
                    fg=self.color_bg
                )
                spacer.grid(row=0, column=columna_actual, padx=2)
                columna_actual += 1
                continue
            
            # Crear slot para letra
            lbl = tk.Label(
                current_row_frame,
                text="",
                font=("Helvetica", 24, "bold"),
                width=2,
                height=1,
                bg=self.color_bg,
                fg="white",
                relief="solid",
                bd=2
            )
            lbl.grid(row=0, column=columna_actual, padx=2)
            
            # Obtener índice usando lenCad indirectamente
            slot_index_str = "".join(str(x) for x in range(len(self.slots))) if self.slots else ""
            slot_index = lib.lenCad(slot_index_str.encode()) // 2  # Aproximación
            lbl.bind("<Button-1>", lambda e, idx=slot_index: self.remover_letra(idx))
            self.slots.append(lbl)
            columna_actual += 1
        
        if current_row_frame:
            current_row_frame.pack()

    def manejar_tecla(self, event):
        """Maneja la entrada por teclado"""
        if event.keysym == "Return" or event.keysym == "KP_Enter":
            self.validar()
            return
        
        if event.keysym == "BackSpace" or event.keysym == "Delete":
            # Encontrar el último slot con letra usando lenCad indirectamente
            for i in range(len(self.slots) - 1, -1, -1):
                texto = self.slots[i].cget("text")
                texto_b = texto.encode() if texto else b""
                if lib.lenCad(texto_b) > 0 and not self.letras_bloqueadas[i]:
                    self.remover_letra(i)
                    break
            return
        
        letra = event.char.upper()
        if letra.isalpha() and len(letra) == 1:
            # Verificar si la letra está en las disponibles
            letra_b = letra.encode()
            disponibles_b = self.letras_disponibles.encode()
            if lib.charInCad(letra_b, disponibles_b) == 1:
                self.colocar_letra(letra)

    def colocar_letra(self, letra):
        """Coloca una letra en el primer slot disponible"""
        for i, slot in enumerate(self.slots):
            texto = slot.cget("text")
            texto_b = texto.encode() if texto else b""
            if lib.lenCad(texto_b) == 0 and not self.letras_bloqueadas[i]:
                slot.config(text=letra, fg="yellow", bg="#333333")
                break

    def remover_letra(self, index):
        """Remueve una letra del slot especificado"""
        # Convertir índice a string para usar lenCad
        slots_indices_str = "".join(str(x) for x in range(len(self.slots))) if self.slots else ""
        slots_indices_b = slots_indices_str.encode()
        max_index = lib.lenCad(slots_indices_b) // 2  # Aproximación
        
        if index < max_index:
            slot = self.slots[index]
            texto = slot.cget("text")
            texto_b = texto.encode() if texto else b""
            if lib.lenCad(texto_b) == 0 or self.letras_bloqueadas[index]:
                return
            slot.config(text="", fg="white", bg=self.color_bg)

    def letraEnPosicion(self, letra, palabra, posicion):
        """Usa la función de la librería para verificar si letra está en posición"""
        if posicion < 0:
            return 0
            
        letra_b = letra.encode()
        palabra_b = palabra.encode()
        palabra_len = lib.lenCad(palabra_b)
        
        if posicion >= palabra_len:
            return 0
            
        return lib.letraEnPosicion(letra_b, palabra_b, posicion)

    def contarOcurrencias(self, letra, palabra):
        """Usa la función de la librería para contar ocurrencias"""
        letra_b = letra.encode()
        palabra_b = palabra.encode()
        return lib.contarOcurrencias(letra_b, palabra_b)

    def validar(self):
        """Valida la palabra ingresada"""
        # Reconstruir la palabra del usuario
        palabra_usuario = ""
        for slot in self.slots:
            texto = slot.cget("text")
            palabra_usuario += texto if texto else ""
        
        palabra_usuario = palabra_usuario.upper()
        palabra_correcta = "".join(ch for ch in self.word if ch != " ")
        
        # Usar lenCad para obtener longitudes
        usuario_b = palabra_usuario.encode()
        correcta_b = palabra_correcta.encode()
        usuario_len = lib.lenCad(usuario_b)
        correcta_len = lib.lenCad(correcta_b)
        
        # Verificar si las longitudes coinciden
        if usuario_len != correcta_len:
            messagebox.showwarning("Incorrecto", f"La palabra debe tener {correcta_len} letras. Tienes {usuario_len}.")
            return
        
        # Usar cmpCad para comparar
        son_iguales = lib.cmpCad(usuario_b, correcta_b)
        
        if son_iguales == 1:
            messagebox.showinfo("¡Correcto!", f"¡Felicidades! Has adivinado:\n{self.categoria}")
            
            # Pintar slots de verde y bloquear todos
            for i, slot in enumerate(self.slots):
                slot.config(bg=self.color_correct, fg="white")
                self.letras_bloqueadas[i] = True
            
            # Deshabilitar validación
            self.btn_validar.config(state="disabled", bg="#666666")
            self.root.unbind("<Key>")
                
        else:
            # Identificar letras en posición correcta usando letraEnPosicion
            letras_correctas_posicion = []
            
            for i in range(usuario_len):
                if i < correcta_len:
                    # Obtener letra del usuario usando lenCad para verificar límites
                    if i < lib.lenCad(palabra_usuario.encode()):
                        letra_usuario = palabra_usuario[i]
                    else:
                        letra_usuario = ""
                    
                    if letra_usuario and self.letraEnPosicion(letra_usuario, palabra_correcta, i) == 1:
                        letras_correctas_posicion.append(i)
            
            # CORRECCIÓN: Bloquear las letras en posición correcta
            # Convertir el array a string para usar lenCad
            letras_bloqueadas_str = "".join("1" if x else "0" for x in self.letras_bloqueadas)
            letras_bloqueadas_len = lib.lenCad(letras_bloqueadas_str.encode())
            
            for i in letras_correctas_posicion:
                # Verificar que el índice esté dentro del rango usando lenCad
                if i < letras_bloqueadas_len:
                    self.letras_bloqueadas[i] = True
                    # Solo cambiar el color si el slot no está vacío
                    if i < len(self.slots):
                        self.slots[i].config(bg=self.color_partial, fg="white")
                        # Quitar el binding para que no se pueda hacer clic
                        self.slots[i].unbind("<Button-1>")
            
            # Contar letras correctas para el mensaje
            # Convertir la lista a string para usar lenCad
            letras_correctas_str = "".join(str(x) for x in letras_correctas_posicion)
            num_correctas = lib.lenCad(letras_correctas_str.encode()) // 2  # Aproximación
            
            if num_correctas > 0:
                mensaje = f"¡Bien! {num_correctas} de {correcta_len} letras están en la posición correcta.\nLas letras correctas se han bloqueado en su lugar."
            else:
                # Verificar si hay letras correctas pero en posición incorrecta
                letras_correctas_incorrecta_pos = []
                for i in range(usuario_len):
                    if i < correcta_len:
                        if i < lib.lenCad(palabra_usuario.encode()):
                            letra = palabra_usuario[i]
                        else:
                            letra = ""
                        if letra:
                            letra_b = letra.encode()
                            if lib.charInCad(letra_b, correcta_b) == 1:
                                letras_correctas_incorrecta_pos.append(i)
                
                if len(letras_correctas_incorrecta_pos) > 0:
                    # Contar letras únicas correctas
                    letras_usuario_unicas = set(palabra_usuario)
                    letras_correctas_count = 0
                    for letra in letras_usuario_unicas:
                        letra_b = letra.encode()
                        if lib.charInCad(letra_b, correcta_b) == 1:
                            letras_correctas_count += 1
                    
                    mensaje = f"{letras_correctas_count} letra(s) son correctas pero están en posición equivocada."
                else:
                    mensaje = "Ninguna letra es correcta. Intenta nuevamente."
            
            messagebox.showwarning("Incorrecto", mensaje)
            
            # Pintar slots incorrectos de rojo temporalmente (excepto los bloqueados)
            for i, slot in enumerate(self.slots):
                if not self.letras_bloqueadas[i]:
                    texto = slot.cget("text")
                    texto_b = texto.encode() if texto else b""
                    if lib.lenCad(texto_b) > 0:
                        slot.config(bg=self.color_incorrect, fg="white")
            
            # Después de 1.5 segundos, limpiar solo los slots no bloqueados
            self.root.after(1500, self.limpiar_slots_no_bloqueados)

    def limpiar_slots_no_bloqueados(self):
        """Limpia los slots que no están bloqueados"""
        for i, slot in enumerate(self.slots):
            if not self.letras_bloqueadas[i]:
                slot.config(text="", fg="white", bg=self.color_bg)


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazDemo(root, dificultad=2)
    root.mainloop()

    #ultima version de artemio