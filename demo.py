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
            except:
                lbl = tk.Label(frame_imgs, text="No img", bg=self.color_panel, fg="white")
                lbl.grid(row=i // 2, column=i % 2, padx=10, pady=10)

        # SLOTS
        self.word = self.categoria.upper()
        self.slots = []
        self.letras_bloqueadas = []
        
        # Frame principal para slots
        frame_slots = tk.Frame(root, bg=self.color_bg)
        frame_slots.pack(pady=20, fill="both", expand=True)
        
        self.crear_slots_organizados(frame_slots)

        # ================================
        # BOTONES DE LETRAS
        # ================================
        frame_btns = tk.Frame(root, bg=self.color_bg)
        frame_btns.pack(pady=20, fill="both", expand=True)
        
        # USAR letrasUnicas PARA OBTENER LETRAS ÚNICAS
        buffer_unicas = ffi.new("char[]", 27)
        lib.letrasUnicas(self.word.replace(" ", "").encode(), buffer_unicas)
        letras_unicas_str = ffi.string(buffer_unicas).decode()
        letras_lista = list(letras_unicas_str)
        
        # USAR contarOcurrencias PARA VERIFICAR
        for letra in set(letras_unicas_str):
            if letra:
                count = lib.contarOcurrencias(letra.encode(), self.word.replace(" ", "").encode())
        
        # Rellenar hasta al menos 12 letras
        todas = set(letras_lista)
        abecedario = [chr(i) for i in range(65, 91)]
        
        while len(letras_lista) < 12:
            nueva = random.choice(abecedario)
            if nueva not in todas:
                letras_lista.append(nueva)
                todas.add(nueva)
        
        # USAR mezclarCadena PARA REVOLVER
        letras_str = "".join(letras_lista)
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
        self.letras_bloqueadas = []
        
        main_slot_frame = tk.Frame(parent_frame, bg=self.color_bg)
        main_slot_frame.pack()
        
        max_slots_por_fila = 15
        columna_actual = 0
        current_row_frame = None
        
        for ch in self.word:
            if columna_actual == 0 or columna_actual >= max_slots_por_fila:
                if current_row_frame:
                    current_row_frame.pack()
                
                current_row_frame = tk.Frame(main_slot_frame, bg=self.color_bg)
                current_row_frame.pack(pady=5)
                columna_actual = 0
            
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
            self.letras_bloqueadas.append(False)
            columna_actual += 1
        
        if current_row_frame:
            current_row_frame.pack()

    # ===================================
    # AGREGAR LETRA
    # ===================================
    def colocar_letra(self, letra):
        for i, slot in enumerate(self.slots):
            if slot.cget("text") == "" and not self.letras_bloqueadas[i]:
                slot.config(text=letra, fg="yellow", bg="#333333")
                
                # Obtener el índice en la palabra sin espacios
                # Primero, necesitamos saber cuántas letras hemos colocado antes
                indice_en_palabra = 0
                for j in range(i):
                    if self.slots[j].cget("text") != "":
                        indice_en_palabra += 1
                
                # USAR charInCad PARA VERIFICAR SI LA LETRA ESTÁ EN LA PALABRA
                letra_b = letra.encode()
                palabra_b = self.word.replace(" ", "").encode()
                esta = lib.charInCad(letra_b, palabra_b)
                
                if esta == 1:
                    # USAR letraEnPosicion PARA VERIFICAR SI ESTÁ EN POSICIÓN CORRECTA
                    # Usar el índice en la palabra sin espacios
                    posicion_correcta = lib.letraEnPosicion(
                        letra_b, 
                        palabra_b, 
                        indice_en_palabra  # Índice en la palabra sin espacios
                    )
                    
                    if posicion_correcta == 1:
                        slot.config(bg="#8bc34a", fg="white")
                
                break

    # ===================================
    # QUITAR LETRA
    # ===================================
    def remover_letra(self, index):
        if index < len(self.slots):
            slot = self.slots[index]
            if slot.cget("text") == "" or self.letras_bloqueadas[index]:
                return
            
            slot.config(text="", fg="white", bg=self.color_bg)

    # ===================================
    # VALIDAR - USANDO SOLO FUNCIONES C
    # ===================================
    def validar(self):
        # Reconstruir palabra del usuario
        palabra_usuario = ""
        for slot in self.slots:
            texto = slot.cget("text")
            palabra_usuario += texto if texto else ""
        
        palabra_usuario = palabra_usuario.upper()
        palabra_correcta = "".join(ch for ch in self.word if ch != " ")
        
        # USAR cmpCadIgnoreCase PARA COMPARACIÓN FLEXIBLE
        usuario_b = palabra_usuario.encode()
        correcta_b = palabra_correcta.encode()
        
        son_iguales = lib.cmpCadIgnoreCase(usuario_b, correcta_b)
        
        if son_iguales == 1:
            # USAR cmpCad PARA VERIFICAR SI ES EXACTAMENTE IGUAL
            son_exactos = lib.cmpCad(usuario_b, correcta_b)
            
            mensaje = f"¡Felicidades! Has adivinado:\n{self.categoria}"
            if son_exactos != 1:
                mensaje += f"\n(La palabra correcta es: {self.word})"
            
            messagebox.showinfo("¡Correcto!", mensaje)
            
            for i, slot in enumerate(self.slots):
                slot.config(bg=self.color_correct, fg="white")
                self.letras_bloqueadas[i] = True
            
            for btn in self.btn_refs:
                btn.config(state="disabled", bg="#666666")
                
        else:
            # USAR letraEnPosicion PARA IDENTIFICAR LETRAS CORRECTAS
            letras_correctas_posicion = []
            letras_correctas_mal_posicion = []
            
            for i in range(len(palabra_usuario)):
                if i < len(palabra_correcta):
                    letra = palabra_usuario[i]
                    letra_b = letra.encode()
                    
                    # USAR charInCad PARA VERIFICAR SI LA LETRA ESTÁ EN LA PALABRA
                    if lib.charInCad(letra_b, correcta_b) == 1:
                        # USAR letraEnPosicion PARA VERIFICAR POSICIÓN
                        if lib.letraEnPosicion(letra_b, correcta_b, i) == 1:
                            letras_correctas_posicion.append(i)
                        else:
                            letras_correctas_mal_posicion.append(i)
            
            # Bloquear letras en posición correcta
            for i in letras_correctas_posicion:
                self.letras_bloqueadas[i] = True
                self.slots[i].config(bg=self.color_partial, fg="white")
                self.slots[i].unbind("<Button-1>")
            
            # Preparar mensaje usando funciones C
            num_correctas = len(letras_correctas_posicion)
            num_mal_posicion = len(letras_correctas_mal_posicion)
            
            if num_correctas > 0:
                mensaje = f"¡Bien! {num_correctas} letra(s) en posición correcta.\n"
                if num_mal_posicion > 0:
                    mensaje += f"{num_mal_posicion} letra(s) correcta(s) pero en posición equivocada."
            elif num_mal_posicion > 0:
                mensaje = f"{num_mal_posicion} letra(s) correcta(s) pero en posición equivocada."
            else:
                # USAR contarOcurrencias PARA ANÁLISIS DETALLADO
                mensaje = "Letras incorrectas:\n"
                letras_usadas_set = []
                # Crear lista de letras únicas del usuario
                for letra in palabra_usuario:
                    if letra not in letras_usadas_set:
                        letras_usadas_set.append(letra)
                
                for letra in letras_usadas_set:
                    if letra:
                        # Contar ocurrencias en usuario
                        count_usuario = 0
                        for ch in palabra_usuario:
                            if ch == letra:
                                count_usuario += 1
                        
                        # USAR contarOcurrencias PARA OBTENER OCURRENCIAS EN PALABRA CORRECTA
                        count_correcta = lib.contarOcurrencias(letra.encode(), correcta_b)
                        
                        if count_correcta == 0:
                            mensaje += f"'{letra}' no está en la palabra.\n"
                        elif count_usuario > count_correcta:
                            mensaje += f"Demasiadas '{letra}' (tienes {count_usuario}, necesita {count_correcta}).\n"
            
            messagebox.showwarning("Incorrecto", mensaje)
            
            # Resaltar slots incorrectos
            for i, slot in enumerate(self.slots):
                if not self.letras_bloqueadas[i] and slot.cget("text") != "":
                    slot.config(bg=self.color_incorrect, fg="white")
            
            # Limpiar después de 1.5 segundos
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
    app = InterfazDemo(root, dificultad=0)
    root.mainloop()