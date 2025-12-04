import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from cffi import FFI
import _game_lib
import random

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
        self.color_partial = "#ffa500"  # Naranja para letras correctas en posición correcta

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
        
        # Lista para guardar letras bloqueadas en cada slot
        self.letras_bloqueadas = [False] * len([ch for ch in self.word if ch != " "])
        
        # Frame principal para slots
        frame_slots = tk.Frame(root, bg=self.color_bg)
        frame_slots.pack(pady=20, fill="both", expand=True)
        
        self.crear_slots_organizados(frame_slots)

        # ================================
        # BOTONES DE LETRAS
        # ================================
        frame_btns = tk.Frame(root, bg=self.color_bg)
        frame_btns.pack(pady=20, fill="both", expand=True)
        
        # Usar charInCad para verificar si una letra pertenece a la palabra
        letras_correctas = []
        letras_unicas_set = set()
        
        # Verificar cada letra del alfabeto usando charInCad
        palabra_sin_espacios = self.word.replace(" ", "")
        for letra_code in range(65, 91):  # A-Z
            letra = chr(letra_code)
            letra_b = letra.encode()
            palabra_b = palabra_sin_espacios.encode()
            
            # Usar charInCad de la librería C
            if lib.charInCad(letra_b, palabra_b) == 1:
                letras_correctas.append(letra)
                letras_unicas_set.add(letra)
        
        # Rellenar hasta al menos 12 letras
        abecedario = [chr(i) for i in range(65, 91)]
        letras_finales = list(letras_unicas_set)
        
        while len(letras_finales) < 12:
            nueva = random.choice(abecedario)
            if nueva not in letras_finales:
                letras_finales.append(nueva)
        
        # Revolver las letras
        letras_str = "".join(letras_finales)
        buf = ffi.new("char[]", letras_str.encode())
        lib.mezclarCadena(buf)
        revueltas = ffi.string(buf).decode()
        
        # Crear botones
        self.btn_refs = []
        botones_por_fila = 10
        
        for i, letra in enumerate(revueltas):
            btn = tk.Button(
                frame_btns,
                text=letra,
                font=("Helvetica", 18, "bold"),
                width=3,
                height=1,
                bg=self.color_btn,
                fg="white",
                relief="raised"
            )
            btn.config(command=lambda l=letra: self.colocar_letra(l))
            
            fila = i // botones_por_fila
            columna = i % botones_por_fila
            btn.grid(row=fila, column=columna, padx=5, pady=5)
            self.btn_refs.append(btn)
        
        for i in range(botones_por_fila):
            frame_btns.grid_columnconfigure(i, weight=1)

    def crear_slots_organizados(self, parent_frame):
        """Crea slots organizados en filas"""
        self.slots = []
        
        main_slot_frame = tk.Frame(parent_frame, bg=self.color_bg)
        main_slot_frame.pack()
        
        max_slots_por_fila = 15
        fila_actual = 0
        columna_actual = 0
        current_row_frame = None
        
        # Obtener solo letras (sin espacios) para la lista de slots
        palabra_sin_espacios = "".join(ch for ch in self.word if ch != " ")
        
        for i, ch in enumerate(self.word):
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
            
            slot_index = len(self.slots)
            lbl.bind("<Button-1>", lambda e, idx=slot_index: self.remover_letra(idx))
            self.slots.append(lbl)
            columna_actual += 1
        
        if current_row_frame:
            current_row_frame.pack()

    # ===================================
    # AGREGAR LETRA
    # ===================================
    def colocar_letra(self, letra):
        for i, slot in enumerate(self.slots):
            # Solo colocar en slots no bloqueados y vacíos
            if slot.cget("text") == "" and not self.letras_bloqueadas[i]:
                slot.config(text=letra, fg="yellow", bg="#333333")
                break

        # Validar si todos los slots están llenos
        slots_llenos = all(
            slot.cget("text") != "" or self.letras_bloqueadas[i] 
            for i, slot in enumerate(self.slots)
        )
        
        if slots_llenos:
            self.validar()

    # ===================================
    # QUITAR LETRA
    # ===================================
    def remover_letra(self, index):
        if index < len(self.slots):
            slot = self.slots[index]
            # No permitir remover letras bloqueadas
            if slot.cget("text") == "" or self.letras_bloqueadas[index]:
                return

            slot.config(text="", fg="white", bg=self.color_bg)

    # ===================================
    # VALIDAR - CON BLOQUEO DE LETRAS CORRECTAS
    # ===================================
    def validar(self):
        # Reconstruir la palabra del usuario
        palabra_usuario = ""
        for slot in self.slots:
            texto = slot.cget("text")
            palabra_usuario += texto if texto else ""
        
        palabra_usuario = palabra_usuario.upper()
        palabra_correcta = "".join(ch for ch in self.word if ch != " ")
        
        # Usar cmpCad para comparar
        usuario_b = palabra_usuario.encode()
        correcta_b = palabra_correcta.encode()
        son_iguales = lib.cmpCad(usuario_b, correcta_b)
        
        if son_iguales == 1:
            messagebox.showinfo("¡Correcto!", f"¡Felicidades! Has adivinado:\n{self.categoria}")
            
            # Pintar slots de verde y bloquear todos
            for i, slot in enumerate(self.slots):
                slot.config(bg=self.color_correct, fg="white")
                self.letras_bloqueadas[i] = True
            
            # Deshabilitar botones
            for btn in self.btn_refs:
                btn.config(state="disabled", bg="#666666")
                
        else:
            # Identificar letras en posición correcta
            letras_correctas_posicion = []
            
            for i in range(len(palabra_usuario)):
                if i < len(palabra_correcta):
                    # Comparar letra por letra
                    letra_usuario = palabra_usuario[i]
                    letra_correcta = palabra_correcta[i]
                    
                    if letra_usuario == letra_correcta:
                        letras_correctas_posicion.append(i)
            
            # Bloquear las letras en posición correcta
            for i in letras_correctas_posicion:
                self.letras_bloqueadas[i] = True
                # Cambiar color a naranja para indicar letra bloqueada correcta
                self.slots[i].config(bg=self.color_partial, fg="white")
                # Hacer que el slot no sea clickeable
                self.slots[i].unbind("<Button-1>")
            
            # Contar letras correctas para el mensaje
            num_correctas = len(letras_correctas_posicion)
            total_letras = len(palabra_correcta)
            
            if num_correctas > 0:
                mensaje = f"¡Bien! {num_correctas} de {total_letras} letras están en la posición correcta.\nLas letras correctas se han bloqueado en su lugar."
            else:
                # Verificar si hay letras correctas pero en posición incorrecta
                letras_correctas_incorrecta_pos = []
                for i, letra in enumerate(palabra_usuario):
                    if i < len(palabra_correcta):
                        letra_b = letra.encode()
                        if lib.charInCad(letra_b, correcta_b) == 1:
                            letras_correctas_incorrecta_pos.append(i)
                
                if letras_correctas_incorrecta_pos:
                    mensaje = f"Algunas letras son correctas pero están en la posición equivocada."
                else:
                    mensaje = "Ninguna letra es correcta. Intenta nuevamente."
            
            messagebox.showwarning("Incorrecto", mensaje)
            
            # Pintar slots incorrectos de rojo temporalmente (excepto los bloqueados)
            for i, slot in enumerate(self.slots):
                if not self.letras_bloqueadas[i] and slot.cget("text") != "":
                    slot.config(bg=self.color_incorrect, fg="white")
            
            # Después de 1.5 segundos, limpiar solo los slots no bloqueados
            self.root.after(1500, self.limpiar_slots_no_bloqueados)

    # ===================================
    # LIMPIAR SLOTS NO BLOQUEADOS
    # ===================================
    def limpiar_slots_no_bloqueados(self):
        for i, slot in enumerate(self.slots):
            if not self.letras_bloqueadas[i]:
                slot.config(text="", fg="white", bg=self.color_bg)


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = InterfazDemo(root, dificultad=2)
        root.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()