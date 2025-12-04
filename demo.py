from tkinter import messagebox
from PIL import Image, ImageTk
import os
from cffi import FFI
import _game_lib
import tkinter as tk

lib = _game_lib.lib
ffi = FFI()
lib.init_rand_seed() # ← USO DE ASM: Inicializa semilla para números aleatorios

BASE = os.path.abspath(os.path.dirname(__file__))

ARCHIVOS = [
    os.path.join(BASE, "niveles", "facil.txt").encode(),
    os.path.join(BASE, "niveles", "medio.txt").encode(),
    os.path.join(BASE, "niveles", "dificil.txt").encode(),
]

RESULTADOS_FILE = "resultados.txt"

def obtener_categoria(dificultad: int) -> str:
    txt_buffer = ffi.new("char[]", 4096)
    categoria = ffi.new("char[]", 256)

    leidos = lib.leerArchivo(ARCHIVOS[dificultad], txt_buffer, 4096) # ← USO DE ASM: Lee archivo
    if leidos <= 0:
        raise FileNotFoundError(f"No se pudo leer archivo de dificultad {dificultad}")

    lib.obtenerLineaRandom(txt_buffer, categoria) # ← USO DE ASM: Obtiene línea aleatoria
    return ffi.string(categoria).decode().strip()


class InterfazDemo:
    def __init__(self, root, dificultad=0):
        self.root = root
        root.title("4 Imágenes 1 Palabra - Teclado Funcional y Validación")
        root.geometry("900x1000")
        root.configure(bg="#1e1e1e")
        
        self.tiempo_corriendo = False
        self.tiempo_actual_ms = 0
        self.intentos = 0
        self.dificultad = dificultad
        self.dificultad_nombres = ['Fácil','Medio','Difícil']
        
        self.color_bg = "#1e1e1e"
        self.color_panel = "#2b2b2b"
        self.color_text = "#ffffff"
        self.color_correct = "#4caf50"
        self.color_incorrect = "#ff4444"
        self.color_filled = "#444444"
        self.color_empty = "#333333"
        self.color_tiempo = "#FFD700"
        
        self.tiempo_buffer = ffi.new("char[]", 20)

        try:
            self.categoria = obtener_categoria(dificultad)
        except Exception as e:
            messagebox.showerror("Error de Carga", f"No se pudo cargar la palabra. {e}")
            self.root.destroy()
            return
            
        self.word = self.categoria.upper()
        self.carpeta = os.path.join(BASE, "Imagenes", self.categoria)
        
        self.letras_disponibles = self.obtener_letras_disponibles()

        frame_header = tk.Frame(root, bg=self.color_bg)
        frame_header.pack(pady=10, fill="x", padx=20)
        
        tk.Label(
            frame_header,
            text="ADIVINA LA PALABRA",
            font=("Helvetica", 22, "bold"),
            bg=self.color_bg,
            fg=self.color_text
        ).pack(side="left")
        
        self.tiempo_var = tk.StringVar(value="00:00.000")
        self.label_tiempo = tk.Label(
            frame_header,
            textvariable=self.tiempo_var,
            font=("Courier", 16, "bold"),
            bg=self.color_bg,
            fg=self.color_tiempo
        )
        self.label_tiempo.pack(side="right")
        
        palabra_sin_espacios = "".join(ch for ch in self.word if ch != " ")
        longitud = lib.lenCad(palabra_sin_espacios.encode())
        
        tk.Label(
            root,
            text=f"Dificultad: {self.dificultad_nombres[dificultad]} | Letras: {longitud}",
            font=("Helvetica", 12),
            bg=self.color_bg,
            fg="#aaaaaa"
        ).pack(pady=(0, 10))
        
        lenCad_letras_disponibles = lib.lenCad(self.letras_disponibles.encode())
        
        tk.Label(
            root,
            text=f"Letras disponibles ({lenCad_letras_disponibles}): {self.letras_disponibles}",
            font=("Courier", 10),
            bg=self.color_bg,
            fg="#888888"
        ).pack()
        
        frame_imgs = tk.Frame(root, bg=self.color_panel, bd=2, relief="ridge")
        frame_imgs.pack(pady=15)

        if dificultad == 0:
            num_imagenes = 4
        else:
            num_imagenes = 2
        
        for i in range(1, num_imagenes + 1):
            try:
                ruta = os.path.join(self.carpeta, f"img{i}.png")
                img = Image.open(ruta).resize((150, 150))
                tk_img = ImageTk.PhotoImage(img)
                lbl = tk.Label(frame_imgs, image=tk_img, bg=self.color_panel)
                lbl.image = tk_img
                lbl.grid(row=0, column=i-1, padx=10, pady=10)
                self.imagenes_tk.append(tk_img)
            except Exception:
                lbl = tk.Label(frame_imgs, text=f"Img {i} (Faltante)", 
                                bg="#505050", fg="white", width=20, height=8)
                lbl.grid(row=0, column=i-1, padx=10, pady=10)

        num_slots = longitud
        self.slots = []
        self.letras_bloqueadas = [False] * num_slots
        
        frame_slots_container = tk.Frame(root, bg=self.color_bg)
        frame_slots_container.pack(pady=20)
        
        tk.Label(
            frame_slots_container,
            text="Escribe con el teclado",
            font=("Helvetica", 12),
            bg=self.color_bg,
            fg="#2196F3"
        ).pack(pady=(0, 10))
        
        self.crear_slots(frame_slots_container)
        
        frame_letras_ref = tk.Frame(root, bg=self.color_bg)
        frame_letras_ref.pack(pady=10)
        
        tk.Label(
            frame_letras_ref,
            text=f"Puedes usar estas letras:",
            font=("Helvetica", 11),
            bg=self.color_bg,
            fg="#cccccc"
        ).pack()
        
        letras_grupos = [self.letras_disponibles[i:i+10] for i in range(0, len(self.letras_disponibles), 10)]
        for grupo in letras_grupos:
            tk.Label(
                frame_letras_ref,
                text=grupo,
                font=("Courier", 14, "bold"),
                bg=self.color_bg,
                fg="#4CAF50"
            ).pack()

        frame_controles = tk.Frame(root, bg=self.color_bg)
        frame_controles.pack(pady=20)
        
        self.btn_validar = tk.Button(
            frame_controles,
            text="VALIDAR (ENTER)",
            font=("Helvetica", 14, "bold"),
            bg="#4caf50",
            fg="white",
            command=self.validar,
            width=15,
            height=2
        )
        self.btn_validar.pack(side="left", padx=10)
        
        btn_salir = tk.Button(
            frame_controles,
            text="SALIR AL MENÚ",
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            command=self.salir_al_menu,
            width=15,
            height=2
        )
        btn_salir.pack(side="left", padx=10)

        self.root.bind("<Key>", self.manejar_tecla_simple)
        self.root.focus_set()
        
        self.iniciar_temporizador()
        self.actualizar_tiempo()

    def obtener_letras_disponibles(self):
        palabra = self.categoria.upper().replace(" ", "")
        letras_unicas = list(set(palabra))
        
        min_total_letras = 12
        letras_extra = 4
        
        longitud_unicas = len(letras_unicas)
        target_length = min(20, max(min_total_letras, longitud_unicas + letras_extra))
        
        letras_disponibles_set = set(letras_unicas)
        
        while len(letras_disponibles_set) < target_length:
            rand_num = lib.rnd(26) # ← USO DE ASM: Genera número aleatorio entre 0-25
            letra = chr(65 + rand_num)
            letras_disponibles_set.add(letra)
        
        letras_final = list(letras_disponibles_set)
        letras_str = "".join(letras_final)
        
        buffer_len = len(letras_str) + 1
        buffer = ffi.new("char[]", buffer_len)
        buffer_bytes = letras_str.encode('ascii')
        ffi.buffer(buffer)[:len(buffer_bytes)] = buffer_bytes
        
        lib.mezclarCadena(buffer)# ← USO DE ASM: Mezcla aleatoriamente la cadena
        
        return ffi.string(buffer).decode().strip()

    def crear_slots(self, parent):
        self.slots = []
        
        frame_slots = tk.Frame(parent, bg=self.color_bg)
        frame_slots.pack()
        
        col = 0
        row_frame = None
        
        for i, ch in enumerate(self.word):
            if col == 0 or col >= 15:
                if row_frame:
                    row_frame.pack()
                row_frame = tk.Frame(frame_slots, bg=self.color_bg)
                row_frame.pack(pady=5)
                col = 0
            
            if ch == " ":
                tk.Label(row_frame, text="    ", bg=self.color_bg).grid(row=0, column=col, padx=2)
                col += 1
                continue
            
            slot = tk.Label(
                row_frame,
                text="",
                font=("Helvetica", 24, "bold"),
                width=2,
                height=1,
                bg=self.color_empty,
                fg="white",
                relief="solid",
                bd=2
            )
            slot.grid(row=0, column=col, padx=2)
            slot.bind("<Button-1>", lambda e, idx=len(self.slots): self.remover_letra(idx))
            self.slots.append(slot)
            col += 1
        
        if row_frame:
            row_frame.pack()

    def manejar_tecla_simple(self, event):
        if not self.tiempo_corriendo:
            return

        if event.keysym in ["Return", "KP_Enter"]:
            self.validar()
            return
        
        if event.keysym in ["BackSpace", "Delete"]:
            for i in range(len(self.slots)-1, -1, -1):
                if self.slots[i].cget("text") and not self.letras_bloqueadas[i]:
                    self.remover_letra(i)
                    break
            return
        
        letra = event.char.upper()
        if letra and letra.isalpha():
            if lib.charInCad(letra.encode(), self.letras_disponibles.encode()):
                self.colocar_letra_simple(letra)
        
        self.root.update()

    def colocar_letra_simple(self, letra):
        for i, slot in enumerate(self.slots):
            if not slot.cget("text") and not self.letras_bloqueadas[i]:
                slot.config(text=letra, fg="white", bg=self.color_filled) 
                break
        else:
            print("No hay slots disponibles")

    def remover_letra(self, index):
        if index < len(self.slots) and not self.letras_bloqueadas[index]:
            self.slots[index].config(text="", bg=self.color_empty, fg="white")

    def limpiar_incorrectos(self):
        for i, slot in enumerate(self.slots):
            if not self.letras_bloqueadas[i] and slot.cget("text"):
                slot.config(text="", bg=self.color_empty, fg="white")
                
    def salir_al_menu(self):
        self.root.destroy()
        root = tk.Tk()
        MenuSimple(root)
        root.mainloop()

    def iniciar_temporizador(self):
        lib.iniciar_temporizador()
        self.tiempo_corriendo = True
    
    def actualizar_tiempo(self):
        if self.tiempo_corriendo:
            self.tiempo_actual_ms = lib.obtener_tiempo_actual()
            lib.formato_tiempo_mm_ss(self.tiempo_actual_ms, self.tiempo_buffer)
            tiempo_str = ffi.string(self.tiempo_buffer).decode()
            
            self.tiempo_var.set(f"⏱️ {tiempo_str}")
        
        self.root.after(100, self.actualizar_tiempo)

    def guardar_resultado(self, tiempo_str):
        dificultad_texto = self.dificultad_nombres[self.dificultad]
        
        linea = f"Palabra: {self.categoria} | Dificultad: {dificultad_texto} | Tiempo: {tiempo_str} | Intentos (Errores/Pistas): {self.intentos}\n"
        
        try:
            with open(RESULTADOS_FILE, "a", encoding="utf-8") as f:
                f.write(linea)
            print(f"Resultado guardado en {RESULTADOS_FILE}: {linea.strip()}")
        except Exception as e:
            messagebox.showerror("Error de Archivo", f"No se pudo guardar el resultado. Error: {e}")

    def validar(self):
        palabra_usuario = "".join(slot.cget("text") or "" for slot in self.slots)
        palabra_correcta = self.word.replace(" ", "")
        
        if lib.lenCad(palabra_usuario.encode()) != lib.lenCad(palabra_correcta.encode()):
            messagebox.showwarning("Incompleto", "Debes rellenar todos los espacios para validar.")
            return

        if not palabra_usuario:
            messagebox.showwarning("Vacío", "Ingresa al menos una letra")
            return
        
        usuario_b = palabra_usuario.encode()
        correcta_b = palabra_correcta.encode()
        
        son_iguales = lib.cmpCad(usuario_b, correcta_b)
        
        self.intentos += 1
        
        if son_iguales == 1:
            self.nivel_completado(palabra_usuario)
        else:
            self.analizar_error(palabra_usuario, palabra_correcta)
    
    def nivel_completado(self, palabra_usuario):
        tiempo_final = lib.detener_temporizador()
        self.tiempo_corriendo = False
        
        lib.formato_tiempo_mm_ss(tiempo_final, self.tiempo_buffer)
        tiempo_str = ffi.string(self.tiempo_buffer).decode()
        
        self.guardar_resultado(tiempo_str)

        mensaje = f"🎉 ¡CORRECTO!\n\n"
        mensaje += f"Palabra: {self.categoria}\n"
        mensaje += f"Dificultad: {self.dificultad_nombres[self.dificultad]}\n"
        mensaje += f"Tiempo: {tiempo_str}\n"
        mensaje += f"Intentos (Errores): {self.intentos}\n\n"
        
        messagebox.showinfo("¡Felicidades!", mensaje)
        
        for i, slot in enumerate(self.slots):
            slot.config(bg=self.color_correct, fg="white")
            self.letras_bloqueadas[i] = True
        
        self.btn_validar.config(state="disabled", bg="#666666")
        self.root.unbind("<Key>")
    
    def analizar_error(self, palabra_usuario, palabra_correcta):
        
        posiciones_correctas = 0
        for i in range(min(len(palabra_usuario), len(palabra_correcta))):
            if palabra_usuario[i] == palabra_correcta[i]:
                posiciones_correctas += 1
                if i < len(self.slots):
                    self.letras_bloqueadas[i] = True
                    self.slots[i].config(bg=self.color_correct, fg="white")
            elif i < len(self.slots):
                self.slots[i].config(bg=self.color_incorrect, fg="white")

        correctas_mal_pos = 0
        correctas_en_palabra = set(palabra_correcta)
        for letra_ingresada in set(palabra_usuario):
            if letra_ingresada in correctas_en_palabra and letra_ingresada not in (palabra_correcta[i] for i, b in enumerate(self.letras_bloqueadas) if b):
                correctas_mal_pos += 1
            
        mensaje = f"Intentos: {self.intentos}\n"
        
        if posiciones_correctas > 0:
            mensaje += f" {posiciones_correctas} letra(s) correcta(s) en posición. ¡Bloqueadas!\n"
        
        if correctas_mal_pos > 0:
            mensaje += f"🟡 Hay {correctas_mal_pos} letra(s) que pertenecen a la palabra pero están en mala posición.\n"
        elif posiciones_correctas == 0:
            mensaje += " Ninguna letra correcta en posición."
        
        messagebox.showwarning("Incorrecto", mensaje)
        
        self.root.after(1500, self.limpiar_incorrectos)

class MenuSimple:
    def __init__(self, root):
        self.root = root
        root.title("4 Imágenes 1 Palabra - Menú Principal")
        root.geometry("550x700") 
        root.configure(bg="#1e1e1e")
        
        main_frame = tk.Frame(root, bg="#1e1e1e")
        main_frame.pack(expand=True, padx=20, pady=20)
        
        tk.Label(
            main_frame,
            text="4 IMÁGENES 1 PALABRA ",
            font=("Helvetica", 30, "bold"),
            bg="#1e1e1e",
            fg="#FFC300"
        ).pack(pady=(20, 10))
        
        tk.Label(
            main_frame,
            
            font=("Helvetica", 14, "italic"),
            bg="#1e1e1e",
            fg="#AAAAAA"
        ).pack(pady=(0, 40))
        
        tk.Label(
            main_frame,
            text="Elige la Dificultad:",
            font=("Helvetica", 18, "bold"),
            bg="#1e1e1e",
            fg="#FFFFFF"
        ).pack(pady=(30, 15))
        
        button_style = {
            "font": ("Helvetica", 14, "bold"),
            "width": 25,
            "height": 2,
            "fg": "white",
            "bd": 3,
            "relief": tk.RAISED,
            "activebackground": "#333333",
            "activeforeground": "#FFC300"
        }
        
        btn_facil = tk.Button(
            main_frame,
            text=" FÁCIL (4 Imágenes)",
            bg="#4CAF50",
            command=lambda: self.iniciar(0),
            **button_style
        )
        btn_facil.pack(pady=8)
        
        btn_medio = tk.Button(
            main_frame,
            text=" MEDIO (2 Imágenes)",
            bg="#FF9800",
            command=lambda: self.iniciar(1),
            **button_style
        )
        btn_medio.pack(pady=8)
        
        btn_dificil = tk.Button(
            main_frame,
            text=" DIFÍCIL (2 Imágenes)",
            bg="#F44336",
            command=lambda: self.iniciar(2),
            **button_style
        )
        btn_dificil.pack(pady=8)
        
        btn_resultados = tk.Button(
            main_frame,
            text=" VER RESULTADOS",
            font=("Helvetica", 12, "bold"),
            bg="#2196F3",
            fg="white",
            width=25,
            height=2,
            bd=3,
            relief=tk.RIDGE,
            command=self.mostrar_resultados
        )
        btn_resultados.pack(pady=(25, 10))
        
        tk.Label(
            main_frame,
            text="Presiona una dificultad para empezar a jugar.",
            font=("Helvetica", 11),
            bg="#1e1e1e",
            fg="#888888"
        ).pack(pady=10)

    def iniciar(self, dificultad):
        self.root.destroy()
        root = tk.Tk()
        InterfazDemo(root, dificultad) 
        root.mainloop()

    def mostrar_resultados(self):
        resultados_window = tk.Toplevel(self.root)
        resultados_window.title("Resultados Históricos del Juego")
        resultados_window.configure(bg="#1e1e1e")
        resultados_window.geometry("700x500")
        
        try:
            with open(RESULTADOS_FILE, "r", encoding="utf-8") as f:
                contenido = f.read()
        except FileNotFoundError:
            contenido = "Aún no hay resultados guardados. ¡Juega una partida para empezar!"
        except Exception as e:
            contenido = f"Error al leer el archivo de resultados: {e}"

        frame_texto = tk.Frame(resultados_window, bg="#1e1e1e")
        frame_texto.pack(padx=20, pady=20, fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame_texto, orient=tk.VERTICAL)
        
        text_widget = tk.Text(
            frame_texto,
            font=("Courier", 10),
            bg="#2b2b2b",
            fg="white",
            height=20,
            width=80,
            wrap="word",
            padx=10,
            pady=10,
            yscrollcommand=scrollbar.set
        )
        text_widget.pack(side="left", fill="both", expand=True)
        
        scrollbar.config(command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        
        text_widget.insert(tk.END, "--- Resultados de Partidas ---\n\n")
        text_widget.insert(tk.END, contenido)
        text_widget.config(state=tk.DISABLED)

        tk.Button(
            resultados_window,
            text="Cerrar",
            command=resultados_window.destroy,
            bg="#607D8B",
            fg="white",
            font=("Helvetica", 12, "bold")
        ).pack(pady=(0, 10))


if __name__ == "__main__":
    
    try:
        root = tk.Tk()
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        menu = MenuSimple(root) 
        root.mainloop()
    except Exception as e:
        print(f"Error al ejecutar la aplicación gráfica: {e}")